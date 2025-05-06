# 🎬 Video Assembly Service API

API này cho phép bạn tạo video bằng cách kết hợp audio chính, hình ảnh/video, hiệu ứng chuyển cảnh và nhạc nền. Nó sử dụng [Shotstack](https://shotstack.io) để render video và [Cloudinary](https://cloudinary.com) để lưu trữ audio đã xử lý.

---

## 🚀 Cách chạy ứng dụng

### 1. Cài đặt phụ thuộc

```bash
pip install -r requirements.txt
```

### 2. Tạo file .env
Tạo file .env trong thư mục gốc với nội dung:

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
API mặc định sẽ chạy tại: http://localhost:8000

## 📡 API Endpoints

**GET video-assembly/health**  
Kiểm tra trạng thái server
Response:

```bash
{
  "status": "healthy"
}
```

**POST video-assembly/videos**  
Tạo một video mới bằng các thành phần được cung cấp.  

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
| Trường                 | Kiểu dữ liệu    | Bắt buộc | Mô tả                                                                                                               |
| ---------------------- | --------------- | -------- | ------------------------------------------------------------------------------------------------------------------- |
| `audio_url`            | `HttpUrl (str)` | ✅        | URL đến file audio chính (giọng nói, nội dung chính của video).                                                     |
| `visual_urls`          | `List[HttpUrl]` | ✅        | Danh sách URL ảnh hoặc video dùng để minh họa nội dung.                                                             |
| `effects`              | `List[str]`     | ❌        | Danh sách hiệu ứng áp dụng lần lượt cho các clip (`zoomIn`, `slideLeft`, v.v.). Nếu không có, mặc định là `"fade"`. |
| `background_music_url` | `HttpUrl (str)` | ❌        | URL đến nhạc nền để hòa trộn cùng audio chính.                                                                      |

**Response:**

```bash
{
  "video_id": "b3f2a52e-9c11-4d13-8e23-d51f1710cc63",
  "video_url": "https://shotstack.io/output/final.mp4",
  "duration": 34.5
}
```

## 🧠 Cấu trúc thư mục

```bash
video-assembly/
├── app/
│   ├── main.py               # Điểm khởi động FastAPI
│   ├── api/assembly.py       # Logic gọi API
│   ├── routes/               # Định nghĩa router và endpoint
│   ├── services/             # Dịch vụ xử lý video, mix audio
│   ├── config/settings.py    # Biến môi trường
│   └── ...
├── uploads/                  # Upload tạm thời (nếu cần)
├── downloads/
├── outputs/
├── tests/                    # Unit test
├── requirements.txt
└── README.md                 
```

## 🛠 Dependencies

- FastAPI: Web framework
- Pydantic: Kiểm tra và validate dữ liệu
- Pydub: Xử lý âm thanh
- Requests: Gọi HTTP
- Shotstack SDK: Render video
- Cloudinary SDK: Upload media

## ✅ Kiểm thử
Chạy unit test bằng:

```bash
pytest
```
