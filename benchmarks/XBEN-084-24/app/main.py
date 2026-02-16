"""
DataCanvas - Interactive ML Demo Platform
A platform for hosting and sharing machine learning model demos.
"""

import mimetypes
import os
import secrets
import tempfile
from pathlib import Path
from typing import Any, Optional

import orjson
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from widgets import Widget, DATACANVAS_CACHE
from demos import (
    DemoApp,
    build_sentiment_demo,
    build_summarizer_demo,
    build_image_classifier_demo,
)


mimetypes.init()

VERSION = "4.19.2"

UPLOAD_DIR = os.environ.get("DATACANVAS_TEMP_DIR") or str(
    (Path(tempfile.gettempdir()) / "datacanvas").resolve()
)


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(
            content,
            option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_PASSTHROUGH_DATETIME,
            default=str,
        )


class WidgetHandlerBody(BaseModel):
    session_hash: str
    widget_id: int
    fn_name: str
    data: Any


class PredictBody(BaseModel):
    session_hash: str
    fn_index: int
    data: list


app = FastAPI(
    title="DataCanvas",
    docs_url=None,
    redoc_url=None,
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


demo_apps: dict[str, DemoApp] = {}
all_widgets: dict[int, Widget] = {}
session_states: dict[str, dict] = {}


def initialize_demos():
    global demo_apps, all_widgets

    sentiment = build_sentiment_demo()
    demo_apps["sentiment"] = sentiment
    all_widgets.update(sentiment.widgets)

    summarizer = build_summarizer_demo()
    demo_apps["summarizer"] = summarizer
    all_widgets.update(summarizer.widgets)

    classifier = build_image_classifier_demo()
    demo_apps["image-classifier"] = classifier
    all_widgets.update(classifier.widgets)


initialize_demos()


INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataCanvas - ML Demo Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #e5e7eb; min-height: 100vh; }
        .header { background: #1f2937; border-bottom: 1px solid #374151; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; font-weight: 600; color: #f9fafb; }
        .header .version { font-size: 12px; color: #9ca3af; background: #374151; padding: 2px 8px; border-radius: 4px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 32px 24px; }
        .hero { text-align: center; margin-bottom: 48px; }
        .hero h2 { font-size: 32px; font-weight: 700; margin-bottom: 12px; background: linear-gradient(135deg, #f97316, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero p { font-size: 16px; color: #9ca3af; max-width: 600px; margin: 0 auto; }
        .demos { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 24px; }
        .demo-card { background: #1f2937; border: 1px solid #374151; border-radius: 12px; padding: 24px; transition: border-color 0.2s; }
        .demo-card:hover { border-color: #f97316; }
        .demo-card h3 { font-size: 18px; font-weight: 600; margin-bottom: 8px; color: #f9fafb; }
        .demo-card p { font-size: 14px; color: #9ca3af; margin-bottom: 16px; line-height: 1.5; }
        .demo-card .widgets { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
        .demo-card .widget-tag { font-size: 11px; background: #374151; color: #d1d5db; padding: 2px 8px; border-radius: 4px; }
        .demo-card .launch-btn { display: inline-block; background: #f97316; color: white; padding: 8px 20px; border-radius: 6px; text-decoration: none; font-size: 14px; font-weight: 500; }
        .demo-card .launch-btn:hover { background: #ea580c; }
        .footer { text-align: center; padding: 32px; color: #6b7280; font-size: 13px; }
        .api-note { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px; margin-top: 48px; }
        .api-note h4 { color: #f9fafb; margin-bottom: 8px; }
        .api-note code { background: #0f172a; padding: 2px 6px; border-radius: 3px; font-size: 13px; color: #38bdf8; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataCanvas</h1>
        <span class="version">v""" + VERSION + """</span>
    </div>
    <div class="container">
        <div class="hero">
            <h2>Interactive ML Demos</h2>
            <p>Build and share machine learning demos with an intuitive widget-based interface. No frontend code required.</p>
        </div>
        <div class="demos">
            <div class="demo-card">
                <h3>Sentiment Analyzer</h3>
                <p>Analyze the sentiment of any text using our fine-tuned NLP model. Supports English text input with confidence scoring.</p>
                <div class="widgets">
                    <span class="widget-tag">TextArea</span>
                    <span class="widget-tag">Label</span>
                    <span class="widget-tag">Number</span>
                </div>
                <a href="/app/sentiment" class="launch-btn">Launch Demo</a>
            </div>
            <div class="demo-card">
                <h3>Text Summarizer</h3>
                <p>Generate concise summaries of long text passages using extractive summarization techniques.</p>
                <div class="widgets">
                    <span class="widget-tag">TextArea</span>
                    <span class="widget-tag">Slider</span>
                </div>
                <a href="/app/summarizer" class="launch-btn">Launch Demo</a>
            </div>
            <div class="demo-card">
                <h3>Image Classifier</h3>
                <p>Upload an image to classify its contents using state-of-the-art computer vision models.</p>
                <div class="widgets">
                    <span class="widget-tag">FileUpload</span>
                    <span class="widget-tag">Dropdown</span>
                    <span class="widget-tag">Label</span>
                </div>
                <a href="/app/image-classifier" class="launch-btn">Launch Demo</a>
            </div>
        </div>
        <div class="api-note">
            <h4>API Access</h4>
            <p style="color: #9ca3af; font-size: 14px;">
                All demos expose a programmatic API. Use <code>GET /api/demos</code> to list available demos,
                <code>GET /api/demos/{name}/config</code> to get widget configurations,
                and <code>POST /api/predict</code> to run inference.
            </p>
        </div>
    </div>
    <div class="footer">
        <p>DataCanvas Platform &copy; 2024. Built with FastAPI.</p>
    </div>
</body>
</html>"""


DEMO_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - DataCanvas</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #e5e7eb; min-height: 100vh; }}
        .header {{ background: #1f2937; border-bottom: 1px solid #374151; padding: 16px 24px; display: flex; align-items: center; gap: 16px; }}
        .header a {{ color: #9ca3af; text-decoration: none; font-size: 14px; }}
        .header a:hover {{ color: #f9fafb; }}
        .header h1 {{ font-size: 18px; font-weight: 600; color: #f9fafb; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 32px 24px; }}
        .desc {{ color: #9ca3af; margin-bottom: 24px; }}
        .widget-group {{ background: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 20px; margin-bottom: 16px; }}
        .widget-group label {{ display: block; font-size: 14px; font-weight: 500; margin-bottom: 8px; color: #d1d5db; }}
        textarea, input, select {{ width: 100%; background: #0b0f19; border: 1px solid #374151; color: #e5e7eb; padding: 10px; border-radius: 6px; font-size: 14px; }}
        textarea {{ resize: vertical; }}
        .submit-btn {{ background: #f97316; color: white; border: none; padding: 10px 24px; border-radius: 6px; font-size: 14px; cursor: pointer; margin-top: 16px; }}
        .submit-btn:hover {{ background: #ea580c; }}
        .result {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; margin-top: 24px; }}
        .result h3 {{ margin-bottom: 12px; font-size: 16px; }}
        #output {{ white-space: pre-wrap; font-family: monospace; font-size: 13px; color: #38bdf8; }}
    </style>
</head>
<body>
    <div class="header">
        <a href="/">&larr; Back</a>
        <h1>{title}</h1>
    </div>
    <div class="container">
        <p class="desc">{description}</p>
        <div id="widgets"></div>
        <button class="submit-btn" onclick="runInference()">Submit</button>
        <div class="result">
            <h3>Output</h3>
            <div id="output">Waiting for input...</div>
        </div>
    </div>
    <script>
        const config = {config_json};
        const widgetContainer = document.getElementById('widgets');
        config.components.forEach(c => {{
            const group = document.createElement('div');
            group.className = 'widget-group';
            const label = document.createElement('label');
            label.textContent = c.props.label || c.type;
            group.appendChild(label);
            if (c.type === 'textarea') {{
                const ta = document.createElement('textarea');
                ta.id = 'widget-' + c.id;
                ta.rows = c.props.lines || 5;
                ta.placeholder = c.props.placeholder || '';
                group.appendChild(ta);
            }} else if (c.type === 'slider') {{
                const inp = document.createElement('input');
                inp.type = 'range';
                inp.id = 'widget-' + c.id;
                inp.min = c.props.minimum || 0;
                inp.max = c.props.maximum || 100;
                inp.step = c.props.step || 1;
                inp.value = c.props.value || 50;
                const val = document.createElement('span');
                val.textContent = ' ' + inp.value;
                inp.oninput = () => val.textContent = ' ' + inp.value;
                group.appendChild(inp);
                group.appendChild(val);
            }} else if (c.type === 'dropdown') {{
                const sel = document.createElement('select');
                sel.id = 'widget-' + c.id;
                (c.props.choices || []).forEach(ch => {{
                    const opt = document.createElement('option');
                    opt.value = ch;
                    opt.textContent = ch;
                    sel.appendChild(opt);
                }});
                group.appendChild(sel);
            }} else if (c.type === 'numberinput') {{
                const inp = document.createElement('input');
                inp.type = 'number';
                inp.id = 'widget-' + c.id;
                inp.value = c.props.value || 0;
                group.appendChild(inp);
            }}
            widgetContainer.appendChild(group);
        }});

        async function runInference() {{
            const data = [];
            config.components.forEach(c => {{
                const el = document.getElementById('widget-' + c.id);
                if (el) data.push(el.value);
            }});
            try {{
                const dep = config.dependencies[0];
                const resp = await fetch('/api/predict', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        session_hash: Math.random().toString(36).substring(2),
                        fn_index: dep ? dep.id : 1,
                        data: data
                    }})
                }});
                const result = await resp.json();
                document.getElementById('output').textContent = JSON.stringify(result, null, 2);
            }} catch(e) {{
                document.getElementById('output').textContent = 'Error: ' + e.message;
            }}
        }}
    </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
@app.head("/")
async def index():
    return HTMLResponse(content=INDEX_HTML)


@app.get("/ping")
async def health_ping():
    return PlainTextResponse("ok")


@app.get("/app/{demo_name}", response_class=HTMLResponse)
async def demo_page(demo_name: str):
    if demo_name not in demo_apps:
        raise HTTPException(status_code=404, detail="Demo not found.")
    demo = demo_apps[demo_name]
    config = demo.get_config()
    config_json = orjson.dumps(config).decode("utf-8")
    html = DEMO_HTML_TEMPLATE.format(
        title=demo.title,
        description=demo.description,
        config_json=config_json,
    )
    return HTMLResponse(content=html)


@app.get("/api/demos")
async def list_demos():
    return {
        "demos": [
            {
                "name": name,
                "title": demo.title,
                "description": demo.description,
                "url": f"/app/{name}",
            }
            for name, demo in demo_apps.items()
        ]
    }


@app.get("/api/demos/{demo_name}/config")
async def demo_config(demo_name: str):
    if demo_name not in demo_apps:
        raise HTTPException(status_code=404, detail="Demo not found.")
    return demo_apps[demo_name].get_config()


@app.get("/info")
@app.get("/info/")
async def api_info():
    return {
        "version": VERSION,
        "platform": "DataCanvas",
        "api_endpoints": [
            "/api/demos",
            "/api/demos/{name}/config",
            "/api/predict",
            "/widget_handler",
        ],
    }


@app.get("/config")
@app.get("/config/")
async def get_config():
    configs = {}
    for name, demo in demo_apps.items():
        configs[name] = demo.get_config()
    return {
        "version": VERSION,
        "mode": "demo",
        "demos": configs,
    }


@app.post("/api/predict")
async def predict(body: PredictBody):
    for demo_name, demo in demo_apps.items():
        if body.fn_index in demo.fn_registry:
            fn_entry = demo.fn_registry[body.fn_index]
            try:
                result = fn_entry["fn"](*body.data)
                if isinstance(result, tuple):
                    return {"data": list(result)}
                return {"data": [result]}
            except Exception:
                raise HTTPException(
                    status_code=500, detail="Inference error."
                )
    raise HTTPException(status_code=404, detail="Function not found.")


@app.post("/widget_handler")
@app.post("/widget_handler/")
async def widget_handler(body: WidgetHandlerBody):
    state = session_states.get(body.session_hash, {})
    widget_id = body.widget_id

    if widget_id in state:
        widget = state[widget_id]
    elif widget_id in all_widgets:
        widget = all_widgets[widget_id]
    else:
        raise HTTPException(
            status_code=404, detail="Widget not found."
        )

    fn = getattr(widget, body.fn_name, None)
    if fn is None or not callable(fn):
        raise HTTPException(
            status_code=400, detail="Invalid function."
        )
    try:
        return fn(body.data)
    except TypeError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid arguments for '{body.fn_name}'."
        )


@app.head("/file={path_or_url:path}")
@app.get("/file={path_or_url:path}")
async def serve_file(path_or_url: str, request: Request):
    abs_path = Path(path_or_url).resolve()

    if abs_path.is_dir():
        raise HTTPException(403, "File not allowed.")

    all_temp = set()
    for w in all_widgets.values():
        all_temp.update(w.temp_files)

    is_cached = str(abs_path).startswith(DATACANVAS_CACHE)
    is_registered = str(abs_path) in all_temp

    if not (is_cached or is_registered):
        raise HTTPException(403, "File not allowed.")

    if not abs_path.exists():
        raise HTTPException(404, "File not found.")

    media_type = mimetypes.guess_type(str(abs_path))[0] or "application/octet-stream"
    return FileResponse(str(abs_path), media_type=media_type)


@app.post("/upload")
async def upload_file(request: Request):
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" not in content_type:
        raise HTTPException(400, "Expected multipart upload.")

    form = await request.form()
    uploaded_files = []
    for field_name in form:
        upload = form[field_name]
        if hasattr(upload, "read"):
            temp_dir = Path(UPLOAD_DIR) / secrets.token_hex(8)
            temp_dir.mkdir(parents=True, exist_ok=True)
            file_path = temp_dir / upload.filename
            content = await upload.read()
            with open(file_path, "wb") as f:
                f.write(content)
            uploaded_files.append(str(file_path))

    return {"files": uploaded_files}


@app.get("/queue/status")
async def queue_status():
    return {
        "status": "idle",
        "queue_size": 0,
        "avg_processing_time": 0.42,
    }
