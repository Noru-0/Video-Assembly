from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    shotstack_api_key: str
    shotstack_api_host: str = "https://api.shotstack.io/stage"

    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
