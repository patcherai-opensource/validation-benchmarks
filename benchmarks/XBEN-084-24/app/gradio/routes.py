"""
Route definitions for the Gradio-compatible ML interface.
Provides API endpoints for component interaction and model inference.
"""

import json
import os
import random
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from gradio.blocks import BlockContext, Textbox, Image, Number, Label, Button


templates = Jinja2Templates(directory="templates")

# Initialize the block context and demo components
block_context = BlockContext()


def _build_demo():
    """Build the demo interface with components for the sentiment analysis model."""
    # Component 0: Text input for review
    text_input = Textbox(
        block_context,
        label="Customer Review",
        placeholder="Enter a product review to analyze sentiment...",
        lines=4,
        elem_id="review-input",
    )

    # Component 1: Label output for sentiment
    sentiment_output = Label(
        block_context,
        label="Sentiment Analysis",
        num_top_classes=3,
        elem_id="sentiment-output",
    )

    # Component 2: Number output for confidence
    confidence_output = Number(
        block_context,
        label="Confidence Score",
        minimum=0.0,
        maximum=1.0,
        elem_id="confidence-output",
    )

    # Component 3: Submit button
    submit_btn = Button(
        block_context,
        value="Analyze Sentiment",
        variant="primary",
        elem_id="submit-btn",
    )

    # Component 4: Text input for feedback
    feedback_input = Textbox(
        block_context,
        label="Feedback",
        placeholder="Any feedback on the analysis?",
        lines=2,
        elem_id="feedback-input",
    )

    # Component 5: Image for brand logo
    brand_image = Image(
        block_context,
        label="",
        source="upload",
        elem_id="brand-logo",
    )

    return {
        "text_input": text_input,
        "sentiment_output": sentiment_output,
        "confidence_output": confidence_output,
        "submit_btn": submit_btn,
        "feedback_input": feedback_input,
        "brand_image": brand_image,
    }


demo_components = _build_demo()


def _analyze_sentiment(text: str) -> dict:
    """Simple rule-based sentiment analysis for demo purposes."""
    positive_words = [
        "good", "great", "excellent", "amazing", "wonderful", "fantastic",
        "love", "best", "perfect", "happy", "recommend", "quality",
        "beautiful", "awesome", "outstanding", "superb", "pleased",
    ]
    negative_words = [
        "bad", "terrible", "awful", "horrible", "worst", "hate",
        "poor", "disappointed", "broken", "waste", "useless", "defective",
        "ugly", "cheap", "refund", "complaint", "disappointing",
    ]

    text_lower = text.lower()
    words = text_lower.split()

    pos_count = sum(1 for w in words if w.strip(".,!?;:") in positive_words)
    neg_count = sum(1 for w in words if w.strip(".,!?;:") in negative_words)
    total = max(pos_count + neg_count, 1)

    if pos_count > neg_count:
        label = "Positive"
        confidence = 0.55 + (pos_count / total) * 0.40 + random.uniform(-0.03, 0.03)
    elif neg_count > pos_count:
        label = "Negative"
        confidence = 0.55 + (neg_count / total) * 0.40 + random.uniform(-0.03, 0.03)
    else:
        label = "Neutral"
        confidence = 0.45 + random.uniform(-0.05, 0.05)

    confidence = max(0.0, min(1.0, confidence))

    confidences = []
    remaining = 1.0 - confidence
    for lbl in ["Positive", "Negative", "Neutral"]:
        if lbl == label:
            confidences.append({"label": lbl, "confidence": round(confidence, 4)})
        else:
            share = remaining * random.uniform(0.3, 0.7)
            confidences.append({"label": lbl, "confidence": round(min(share, remaining), 4)})
            remaining -= share

    confidences.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "label": label,
        "confidences": confidences,
    }


class ComponentServerRequest(BaseModel):
    component_id: int
    fn_name: str
    data: Any


class PredictRequest(BaseModel):
    data: List[Any]
    fn_index: Optional[int] = 0
    session_hash: Optional[str] = None


def register_routes(app: FastAPI):
    """Register all application routes."""

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/info")
    async def app_info():
        return {
            "version": "4.19.2",
            "mode": "blocks",
            "app_id": "manapool-sentiment-demo",
            "dev_mode": False,
            "analytics_enabled": False,
        }

    @app.get("/config")
    async def get_config():
        components = []
        for block_id, block in block_context.blocks.items():
            components.append(block.get_config())
        return {
            "mode": "blocks",
            "components": components,
            "theme": "default",
            "css": None,
            "title": "Manapool - Sentiment Analysis Demo",
            "description": "Analyze customer review sentiment using our ML model",
            "layout": {
                "id": 0,
                "children": [c["id"] for c in components],
            },
            "dependencies": [
                {
                    "targets": [3],
                    "inputs": [0],
                    "outputs": [1, 2],
                    "fn_index": 0,
                }
            ],
        }

    @app.post("/api/predict")
    async def predict(request: PredictRequest):
        if not request.data or len(request.data) < 1:
            raise HTTPException(status_code=422, detail="Missing input data")

        text = str(request.data[0])
        if not text.strip():
            raise HTTPException(status_code=422, detail="Empty input text")

        result = _analyze_sentiment(text)
        confidence_val = result["confidences"][0]["confidence"] if result["confidences"] else 0.5

        return {
            "data": [result, confidence_val],
            "duration": round(random.uniform(0.05, 0.2), 3),
            "is_generating": False,
        }

    @app.post("/component_server/")
    async def component_server(request: ComponentServerRequest):
        block = block_context.get_block(request.component_id)
        if block is None:
            raise HTTPException(
                status_code=404,
                detail=f"Component {request.component_id} not found"
            )

        fn = getattr(block, request.fn_name, None)
        if fn is None or not callable(fn):
            raise HTTPException(
                status_code=404,
                detail=f"Method {request.fn_name} not found on component"
            )

        try:
            if isinstance(request.data, list):
                result = fn(*request.data)
            elif isinstance(request.data, dict):
                result = fn(**request.data)
            else:
                result = fn(request.data)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")

        return {"data": result}

    @app.post("/api/feedback")
    async def submit_feedback(request: Request):
        body = await request.json()
        feedback_text = body.get("feedback", "")
        if not feedback_text:
            raise HTTPException(status_code=422, detail="Feedback text required")
        return {"status": "ok", "message": "Thank you for your feedback"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}
