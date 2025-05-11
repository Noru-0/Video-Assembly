from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from app.services.video_service import create_video
from uuid import uuid4

router = APIRouter()  # Create a new router for this module

class VideoRequest(BaseModel):
    audio_urls: List[HttpUrl]
    visual_urls: List[HttpUrl]
    effects: Optional[List[str]] = ["fade"]
    transitions: Optional[List[str]] = ["fade"]
    background_music_url: Optional[HttpUrl] = None

class VideoResponse(BaseModel):
    video_id: str
    video_url: Optional[str]
    duration: Optional[float]

@router.post("/videos", response_model=VideoResponse)
async def assemble_video(request: VideoRequest):
    try:
        video_id = str(uuid4())
        video_url, duration = await create_video(
            video_id,
            request.audio_urls,
            request.visual_urls,
            request.effects,
            request.transitions,
            request.background_music_url
        )
        return {"video_id": video_id, "video_url": video_url, "duration": duration}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
