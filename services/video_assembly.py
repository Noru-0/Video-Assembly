import json
import requests
from typing import List, Dict
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import tempfile
import cloudinary
import cloudinary.uploader
import logging 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

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
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
        temp_file.write(response.content)
        return AudioSegment.from_mp3(temp_file.name)

def combine_audio_files(audio_urls: List[str]) -> str:
    """Combine multiple audio files into one and return the URL."""
    # Download and combine all audio segments
    combined = AudioSegment.empty()
    for url in audio_urls:
        segment = download_audio(url)
        combined += segment
    
    # Save the combined audio to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
        combined.export(temp_file.name, format='mp3')
        return temp_file.name

def upload_to_cloudinary(file_path: str) -> str:
    """Upload a file to Cloudinary and return the URL."""
    result = cloudinary.uploader.upload(
        file_path,
        resource_type="video",  # Use video resource type for audio files
        folder="video-assembly"
    )
    return result['secure_url']

def create_video_assembly_request(script_data: Dict) -> Dict:
    """Create the video assembly request payload."""
    # Extract all scene images
    visual_urls = [
        scene["cloudinary_url"] 
        for scene in script_data["image_data"]["scene_images"]
    ]
    
    # Get all audio URLs and combine them
    audio_urls = [
        voiceover["cloudinary_url"]
        for voiceover in script_data["voice_data"]["scene_voiceovers"]
    ]
    
    # Combine all audio files
    combined_audio_path = combine_audio_files(audio_urls)
    
    # Upload combined audio to Cloudinary
    audio_url = upload_to_cloudinary(combined_audio_path)
    
    # Create the request payload
    return {
        "visual_urls": visual_urls,
        "audio_url": audio_url,
        "effects": ["fade"],  # Using fade effect for transitions
        "background_music_url": None  # Optional: Add background music URL if desired
    }

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