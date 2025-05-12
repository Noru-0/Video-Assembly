import json
import requests
from typing import List, Dict
import os
import logging 
import tempfile
from pydub import AudioSegment
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_BASE_URL = "https://tkpm.up.railway.app"

def load_script_data(file_path: str) -> Dict:
    """Load and parse the JSON script data."""
    logger.info(f"Attempting to load script from: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        error_msg = f"Script file not found at path: {os.path.abspath(file_path)}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    # Check if file is empty
    if os.path.getsize(file_path) == 0:
        error_msg = f"Script file is empty: {file_path}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            logger.debug(f"File content: {content[:200]}...")  # Log first 200 chars for debugging
            
            if not content.strip():
                error_msg = "File contains only whitespace"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            try:
                data = json.loads(content)
                # Handle both array and single object formats
                if isinstance(data, list):
                    if len(data) == 0:
                        error_msg = "JSON array is empty"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    result = data[0]
                else:
                    result = data
                
                # Validate required fields
                required_fields = ['image_data', 'voice_data']
                missing_fields = [field for field in required_fields if field not in result]
                if missing_fields:
                    error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                logger.info("Successfully loaded script data")
                return result
                
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON format in file: {str(e)}"
                logger.error(error_msg)
                raise json.JSONDecodeError(error_msg, e.doc, e.pos)
            
    except Exception as e:
        error_msg = f"Unexpected error loading script: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def download_audio(url: str) -> AudioSegment:
    """Download and load an audio file."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download audio: {response.status_code}")
    
    audio_format = url.split(".")[-1].lower()
    return AudioSegment.from_file(io.BytesIO(response.content), format=audio_format)

def combine_audio_files(audio_urls: List[str]) -> str:
    """Combine multiple audio files into one and return the path to the combined file."""
    logger.info("Starting audio combination process")
    
    # Download and combine all audio segments
    combined = AudioSegment.empty()
    for i, url in enumerate(audio_urls):
        logger.info(f"Downloading audio segment {i+1}/{len(audio_urls)}")
        segment = download_audio(url)
        combined += segment
    
    # Save the combined audio to a temporary file
    logger.info("Saving combined audio to temporary file")
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
        combined.export(temp_file.name, format='mp3')
        return temp_file.name

def create_video_assembly_request(script_data: Dict) -> Dict:
    """Create the video assembly request payload."""
    try:
        logger.info("Creating video assembly request payload")
        
        # Extract all scene images
        visual_urls = []
        for scene in script_data["image_data"]["scene_images"]:
            if "cloudinary_url" not in scene:
                logger.warning(f"Scene missing cloudinary_url: {scene}")
                continue
            visual_urls.append(scene["cloudinary_url"])
        
        if not visual_urls:
            raise ValueError("No valid image URLs found in script data")
        
        logger.info(f"Found {len(visual_urls)} valid image URLs")
        
        # Get all audio URLs
        audio_urls = []
        for voiceover in script_data["voice_data"]["scene_voiceovers"]:
            if "cloudinary_url" not in voiceover:
                logger.warning(f"Voiceover missing cloudinary_url: {voiceover}")
                continue
            audio_urls.append(voiceover["cloudinary_url"])
        
        if not audio_urls:
            raise ValueError("No valid audio URLs found in script data")
        
        logger.info(f"Found {len(audio_urls)} valid audio URLs")
    
        # Create the request payload
        payload = {
            "visual_urls": visual_urls,
            "audio_urls": audio_urls,  # Send all audio URLs
            "effects": ["fade"],  # Using fade effect for transitions
            "background_music_url": None,  # Optional: Add background music URL if desired
            "metadata": {
                "num_scenes": len(visual_urls),
                "num_audio_segments": len(audio_urls)
            }
        }
        
        logger.info(f"Created request payload with {len(visual_urls)} scenes and {len(audio_urls)} audio segments")
        return payload
        
    except Exception as e:
        logger.error(f"Error creating video assembly request: {str(e)}")
        raise

def assemble_video(script_path: str) -> Dict:
    """Main function to assemble the video."""
    try:
        # Load script data
        logger.info(f"Starting video assembly process for script: {script_path}")
        script_data = load_script_data(script_path)
        logger.info("Script data loaded successfully")
        
        # Create request payload
        logger.info("Creating request payload")
        payload = create_video_assembly_request(script_data)
        logger.info(f"Request payload created: {payload}")
        
        # Make API request
        logger.info(f"Making API request to: {API_BASE_URL}/video-assembly/videos")
        response = requests.post(
            f"{API_BASE_URL}/video-assembly/videos",
            json=payload
        )
        
        if response.status_code == 200:
            logger.info("Video assembly request successful")
            return response.json()
        else:
            logger.error(f"API request failed with status {response.status_code}: {response.text}")
            raise Exception(f"Failed to create video: {response.text}")
            
    except Exception as e:
        logger.error(f"Error in assemble_video: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Path to your JSON script file
        script_path = "jsonformatter.txt"
        logger.info(f"Starting video assembly with script: {script_path}")
        
        # Assemble the video
        result = assemble_video(script_path)
        
        logger.info("Video creation completed successfully!")
        print("Video creation initiated successfully!")
        print(f"Video ID: {result['video_id']}")
        print(f"Video URL: {result['video_url']}")
        print(f"Duration: {result['duration']} seconds")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"Error: {str(e)}")