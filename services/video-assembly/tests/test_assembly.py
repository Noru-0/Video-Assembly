import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

# Health check test (no changes needed)
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# Mocked Shotstack API call for testing the video assembly functionality
@pytest.mark.skip(reason="Requires Shotstack API key and mocking")
@patch("app.services.video_service.create_video")  # Mock the create_video function
def test_assemble_video(mock_create_video):
    # Define the payload with the updated content
    payload = {
        "audio_url": "https://res.cloudinary.com/dvnr2fqlk/video/upload/v1746259083/harvard_gkg0dq.wav",
        "visual_urls": [
            "https://res.cloudinary.com/dvnr2fqlk/image/upload/v1746232588/sample_image_1_vmitvz.jpg",
            "https://res.cloudinary.com/dvnr2fqlk/image/upload/v1746232589/sample_image_2_cph05i.jpg",
            "https://res.cloudinary.com/dvnr2fqlk/video/upload/v1746232979/sample_video_5s_l0ybyh.mp4",
            "https://res.cloudinary.com/dvnr2fqlk/video/upload/v1746233001/sample_video_10s_hu1ngr.mp4"
        ],
        "effects": ["fade"],
        "background_music_url": "https://res.cloudinary.com/dvnr2fqlk/video/upload/v1746232501/sample_audio_19s_yo8qxx.mp3"
    }
    
    # Mock response for the create_video function
    mock_create_video.return_value = ("https://mocked-video-url.com/video.mp4", 40.0)

    response = client.post("/videos", json=payload)
    
    # Assertions to check the response from the mock
    assert response.status_code == 200
    response_json = response.json()
    assert "video_id" in response_json
    assert response_json["video_url"] == "https://mocked-video-url.com/video.mp4"
    assert response_json["duration"] == 40.0
