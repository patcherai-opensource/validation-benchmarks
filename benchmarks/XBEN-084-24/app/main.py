import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from gradio.routes import register_routes

app = FastAPI(
    title="Manapool ML Platform",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

register_routes(app)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/upload_cache", StaticFiles(directory="upload_cache"), name="upload_cache")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
