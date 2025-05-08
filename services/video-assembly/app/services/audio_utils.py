import os
import uuid
import io
import logging
import requests
import cloudinary
import cloudinary.uploader
from pydub import AudioSegment
from app.config.settings import Settings
import tempfile

# Cấu hình logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Cấu hình Cloudinary
def configure_cloudinary():
    try:
        settings = Settings()
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret
        )
    except Exception as e:
        logger.error(f"Error in Cloudinary configuration: {str(e)}")
        raise

# Hàm trộn nhạc nền và âm thanh chính
def mix_audio(main_audio_url: str, background_music_url: str) -> str:
    """
    Gộp audio chính và nhạc nền, upload lên Cloudinary, trả về URL.
    """
    try:
        # Kiểm tra Cloudinary đã cấu hình chưa
        configure_cloudinary()

        # Tải và đọc dữ liệu từ URLs
        main_audio_response = requests.get(main_audio_url)
        background_audio_response = requests.get(background_music_url)

        # Kiểm tra status code
        if main_audio_response.status_code != 200:
            logger.error(f"Failed to download main audio: {main_audio_response.status_code}")
            raise Exception("Failed to download main audio")
        
        if background_audio_response.status_code != 200:
            logger.error(f"Failed to download background audio: {background_audio_response.status_code}")
            raise Exception("Failed to download background audio")

        # Xác định định dạng file audio
        main_audio_format = main_audio_url.split('.')[-1].lower()
        background_audio_format = background_music_url.split('.')[-1].lower()

        # Đọc audio với pydub
        main_audio = AudioSegment.from_file(io.BytesIO(main_audio_response.content), format=main_audio_format)
        background_audio = AudioSegment.from_file(io.BytesIO(background_audio_response.content), format=background_audio_format)

        # Lặp lại background nếu nó ngắn hơn main audio
        if len(background_audio) < len(main_audio):
            background_audio = background_audio * (len(main_audio) // len(background_audio) + 1)
        background_audio = background_audio[:len(main_audio)]

        # Giảm âm lượng nhạc nền
        background_audio = background_audio - 15

        # Trộn 2 âm thanh lại với nhau
        mixed = main_audio.overlay(background_audio)

        # Tạo file tạm thời
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        mixed.export(temp_file.name, format="mp3")
        temp_filename = temp_file.name
        temp_file.close()

        # Upload lên Cloudinary
        upload_result = cloudinary.uploader.upload(temp_filename, resource_type="video")
        os.remove(temp_filename)

        logger.info(f"Audio uploaded successfully. Cloudinary URL: {upload_result['secure_url']}")
        return upload_result["secure_url"]

    except Exception as e:
        logger.error(f"Error in mixing audio: {str(e)}")
        raise

