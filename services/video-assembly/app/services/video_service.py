import time
import logging
import requests
import io
import cloudinary
import cloudinary.uploader

from shotstack_sdk.configuration import Configuration
from shotstack_sdk.api_client import ApiClient
from shotstack_sdk.api import edit_api
from shotstack_sdk.model.timeline import Timeline
from shotstack_sdk.model.track import Track
from shotstack_sdk.model.clip import Clip
from shotstack_sdk.model.video_asset import VideoAsset
from shotstack_sdk.model.image_asset import ImageAsset
from shotstack_sdk.model.soundtrack import Soundtrack
from shotstack_sdk.model.output import Output
from shotstack_sdk.model.edit import Edit
from shotstack_sdk.model.transition import Transition
from app.config.settings import Settings
from app.services.audio_utils import mix_audio  
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

clip_effects = [
    "zoomIn", "zoomInSlow", "zoomInFast", "zoomOut", "zoomOutSlow", "zoomOutFast",
    "slideLeft", "slideLeftSlow", "slideLeftFast", "slideRight", "slideRightSlow", "slideRightFast",
    "slideUp", "slideUpSlow", "slideUpFast", "slideDown", "slideDownSlow", "slideDownFast"
]
soundtrack_effects = ["fadeInFadeOut"]
transition_effects = [
    "fade", "reveal", "wipeLeft", "wipeRight", "zoom", 
    "slideLeft", "slideRight", "slideUp", "slideDown",
    "carouselLeft", "carouselRight", "carouselUp", "carouselDown",
    "shuffleTopRight", "shuffleRightTop",
    "shuffleRightBottom", "shuffleBottomRight",
    "shuffleBottomLeft", "shuffleLeftBottom", 
    "shuffleLeftTop", "shuffleTopLeft", 
]


# Cấu hình Cloudinary
cloudinary.config(
    cloud_name=Settings().cloudinary_cloud_name,
    api_key=Settings().cloudinary_api_key,
    api_secret=Settings().cloudinary_api_secret
)

async def create_video(video_id: str, audio_url: str, visual_urls: list, effects: list, transitions: list, background_music_url: str = None):
    # Convert HttpUrl to str
    audio_url = str(audio_url)
    background_music_url = str(background_music_url) if background_music_url else None
    visual_urls = [str(url) for url in visual_urls]

    settings = Settings()

    configuration = Configuration()
    configuration.host = str(settings.shotstack_api_host)
    configuration.api_key['DeveloperKey'] = str(settings.shotstack_api_key)

    # Download and process main audio
    response = requests.get(audio_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download audio: {response.status_code}")

    audio_format = audio_url.split(".")[-1].lower()
    audio = AudioSegment.from_file(io.BytesIO(response.content), format=audio_format)
    audio_duration = len(audio) / 1000  # milliseconds to seconds

    duration_per_visual = audio_duration / len(visual_urls) if visual_urls else 10.0

    clips = []
    for i, visual_url in enumerate(visual_urls):
        start_time = i * duration_per_visual
        visual_url_str = str(visual_url)

        if visual_url_str.lower().endswith((".jpg", ".jpeg", ".png")):
            asset = ImageAsset(src=visual_url_str)
        else:
            asset = VideoAsset(src=visual_url_str)

        effect = effects[0] if effects and effects[0] in clip_effects else "zoomIn"

        # Prepare clip parameters
        clip_params = {
            "asset": asset,
            "start": start_time,
            "length": duration_per_visual,
            "effect": effect
        }

        # Apply transition if specified and not the last clip
        if i < len(visual_urls) - 1 and transitions:
            transition_effect = transitions[i % len(transitions)]
            if transition_effect in transition_effects:
                clip_params["transition"] = Transition(**{"in": transition_effect})


        clip = Clip(**clip_params)
        clips.append(clip)

    track = Track(clips=clips)
    timeline = Timeline(tracks=[track])

    # Mix audio and background music if needed
    if audio_url and background_music_url:
        mixed_audio_url = mix_audio(audio_url, background_music_url)
        timeline.soundtrack = Soundtrack(
            src=mixed_audio_url,
            effect="fadeInFadeOut"
        )
    elif audio_url:
        timeline.soundtrack = Soundtrack(
            src=audio_url,
            effect="fadeInFadeOut"
        )
    elif background_music_url:
        timeline.soundtrack = Soundtrack(
            src=background_music_url,
            effect="fadeInFadeOut"
        )

    output = Output(format="mp4", resolution="hd", fps=25.0)
    edit = Edit(timeline=timeline, output=output)

    try:
        with ApiClient(configuration) as api_client:
            api_instance = edit_api.EditApi(api_client)
            response = api_instance.post_render(edit)
            render_id = response['response']['id']
            logger.info(f"Render submitted: {render_id}")

            for _ in range(30):
                time.sleep(5)
                render_status = api_instance.get_render(render_id)
                status = render_status['response']['status']
                logger.info(f"Render status: {status}")
                if status == "done":
                    shotstack_url = render_status['response']['url']
                    # Tải video từ Shotstack và tải lên Cloudinary
                    video_response = requests.get(shotstack_url)
                    if video_response.status_code != 200:
                        raise Exception(f"Failed to download video from Shotstack: {video_response.status_code}")

                    # Tải video lên Cloudinary
                    cloudinary_response = cloudinary.uploader.upload(
                        io.BytesIO(video_response.content),
                        resource_type="video",
                        folder="videos",  
                        public_id=video_id,
                        overwrite=True
                    )
                    cloudinary_url = cloudinary_response['secure_url']
                    return cloudinary_url, audio_duration
                if status == "failed":
                    raise Exception("Rendering failed")

    except Exception as e:
        logger.error(f"Render error: {str(e)}")
        raise
