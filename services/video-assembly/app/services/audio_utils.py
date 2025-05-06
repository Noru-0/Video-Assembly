from pydub import AudioSegment
import requests
import uuid
import os
import io
import cloudinary
import cloudinary.uploader

def mix_audio(main_audio_url: str, background_music_url: str) -> str:
    """
    Gộp audio chính và nhạc nền, upload lên Cloudinary, trả về URL.
    """
    # Tải và đọc dữ liệu
    main_audio_response = requests.get(main_audio_url)
    background_audio_response = requests.get(background_music_url)

    main_audio_format = main_audio_url.split('.')[-1].lower()
    background_audio_format = background_music_url.split('.')[-1].lower()

    main_audio = AudioSegment.from_file(io.BytesIO(main_audio_response.content), format=main_audio_format)
    background_audio = AudioSegment.from_file(io.BytesIO(background_audio_response.content), format=background_audio_format)

    # Lặp lại background nếu ngắn hơn main audio
    if len(background_audio) < len(main_audio):
        background_audio = background_audio * (len(main_audio) // len(background_audio) + 1)
    background_audio = background_audio[:len(main_audio)]

    # Giảm âm lượng nhạc nền
    background_audio = background_audio - 15

    # Overlay audio
    mixed = main_audio.overlay(background_audio)

    # Xuất file tạm thời
    temp_filename = f"/tmp/mixed_{uuid.uuid4().hex}.mp3"
    mixed.export(temp_filename, format="mp3")

    # Upload lên Cloudinary
    upload_result = cloudinary.uploader.upload(temp_filename, resource_type="video")
    os.remove(temp_filename)

    return upload_result["secure_url"]
