"""
LoLLMs Discussion Endpoints
Handles discussion management and file uploads for discussions
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from pathlib import Path
import os
import json
import logging
import uuid
from datetime import datetime

from lollms_core.config import LOLLMsConfig

logger = logging.getLogger(__name__)
router = APIRouter()


class DiscussionCreate(BaseModel):
    title: str


class MessageCreate(BaseModel):
    discussion_id: str
    content: str
    sender: str = "user"


@router.get("/list_discussions")
async def list_discussions():
    """List all discussions"""
    config = LOLLMsConfig()
    discussions_path = config.discussions_path
    discussions = []

    if discussions_path.exists():
        for item in sorted(discussions_path.iterdir()):
            if item.is_dir():
                meta_file = item / "metadata.json"
                if meta_file.exists():
                    with open(meta_file) as f:
                        meta = json.load(f)
                    discussions.append(meta)

    return {"discussions": discussions}


@router.post("/new_discussion")
async def new_discussion(data: DiscussionCreate):
    """Create a new discussion"""
    config = LOLLMsConfig()
    disc_id = str(uuid.uuid4())[:8]
    disc_path = config.discussions_path / disc_id

    disc_path.mkdir(parents=True, exist_ok=True)

    metadata = {
        "id": disc_id,
        "title": data.title,
        "created_at": datetime.utcnow().isoformat(),
        "messages": [],
    }
    with open(disc_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return {"status": True, "discussion": metadata}


@router.post("/post_message")
async def post_message(data: MessageCreate):
    """Post a message to a discussion"""
    config = LOLLMsConfig()
    disc_path = config.discussions_path / data.discussion_id

    if not disc_path.exists():
        raise HTTPException(status_code=404, detail="Discussion not found")

    meta_file = disc_path / "metadata.json"
    with open(meta_file) as f:
        metadata = json.load(f)

    message = {
        "id": len(metadata["messages"]),
        "sender": data.sender,
        "content": data.content,
        "timestamp": datetime.utcnow().isoformat(),
    }
    metadata["messages"].append(message)

    with open(meta_file, "w") as f:
        json.dump(metadata, f, indent=2)

    return {"status": True, "message": message}


@router.post("/upload_discussion_file")
async def upload_discussion_file(
    file: UploadFile = File(...),
    discussion_id: str = Form(...)
):
    """Upload a file attachment for a discussion"""
    config = LOLLMsConfig()
    disc_path = config.discussions_path / discussion_id

    if not disc_path.exists():
        raise HTTPException(status_code=404, detail="Discussion not found")

    uploads_dir = disc_path / "uploads"
    uploads_dir.mkdir(exist_ok=True)

    file_path = uploads_dir / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    logger.info(f"File uploaded: {file_path}")

    return {
        "status": True,
        "filename": file.filename,
        "path": str(file_path),
        "size": len(content),
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the general uploads directory"""
    config = LOLLMsConfig()
    uploads_path = config.uploads_path
    uploads_path.mkdir(parents=True, exist_ok=True)

    file_path = uploads_path / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "status": True,
        "filename": file.filename,
        "size": len(content),
    }
