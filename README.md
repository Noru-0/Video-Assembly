# 🎬 Video Assembly Service API

This API allows you to create videos by combining a main audio track, images/videos, transition effects, and background music. It utilizes [Shotstack](https://shotstack.io) for video rendering and [Cloudinary](https://cloudinary.com) for storing processed audio.

---

## 🌐 API Base URL

The API is deployed on Railway and can be accessed at:

**Base URL**: `https://tkpm.up.railway.app`  

---

## 📡 API Endpoints

### **GET /video-assembly/health**  
Checks the server status.

**Request Example**:
```bash
curl https://tkpm.up.railway.app/video-assembly/health
```

**Response**:
```bash
{
  "status": "healthy"
}
```

**POST video-assembly/videos**  
Creates a new video using the provided components. 

**Request Body:**

```bash
{
  "audio_url": "https://example.com/audio.mp3",
  "visual_urls": [
    "https://example.com/image1.jpg",
    "https://example.com/video2.mp4"
  ],
  "effects": ["zoomIn", "slideLeft"],
  "background_music_url": "https://example.com/music.mp3"
}
```

**Request Example:**
```bash
curl -X POST https://tkpm.up.railway.app/video-assembly/videos \
  -H "Content-Type: application/json" \
  -d '{"audio_url": "https://example.com/audio.mp3", "visual_urls": ["https://example.com/image1.jpg", "https://example.com/video2.mp4"], "effects": ["zoomIn", "slideLeft"], "background_music_url": "https://example.com/music.mp3"}'
```

| Field                | Data Type         | Required | Description                                                    |
|----------------------|-------------------|----------|----------------------------------------------------------------|
| audio_url            | HttpUrl (str)     | ✅       | URL to the main audio file (voice, primary video content).      |
| visual_urls          | List[HttpUrl]     | ✅       | List of image or video URLs used to illustrate the content.    |
| effects              | List[str]         | ❌       | List of effects to apply sequentially to clips (zoomIn, slideLeft, etc.). Defaults to "fade" if not provided. |
| background_music_url | HttpUrl (str)     | ❌       | URL to the background music to blend with the main audio.      |


**Response:**

```bash
{
  "video_id": "b3f2a52e-9c11-4d13-8e23-d51f1710cc63",
  "video_url": "https://shotstack.io/output/final.mp4",
  "duration": 34.5
}
```

## 🚀 How to Run the Application (Local Development)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create .env File
Create a .env file in the root directory with the following content:

```bash
SHOTSTACK_API_KEY=your_shotstack_key
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
```

### 3. Khởi động server FastAPI

```bash
uvicorn app.main:app --reload
```
The API will run by default at: http://localhost:8080

## 🧠 Directory Structure

```bash
video-assembly/
├── app/
│   ├── main.py               # FastAPI entry point
│   ├── api/assembly.py       # API logic
│   ├── routes/               # Router and endpoint definitions
│   ├── services/             # Video and audio processing services
│   ├── config/settings.py    # Environment variables
│   └── ...
├── tests/                    # Unit tests
├── requirements.txt
└── README.md                
```

## 🛠 Dependencies

- FastAPI: Web framework
- Pydantic: Data validation
- Pydub: Audio processing
- Requests: HTTP calls
- Shotstack SDK: Video rendering
- Cloudinary SDK: Media upload

## ✅ Testing (Local Development)
Run unit tests with:

```bash
pytest
```

