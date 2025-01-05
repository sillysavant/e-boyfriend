import subprocess
import logging
import os

async def generate_lip_sync(audio_path: str) -> bool:
    """
    Generates lip-sync data using Rhubarb.
    
    Args:
        audio_path (str): Path to the input audio file
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Verify audio file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    # Ensure output directory exists
    os.makedirs("static", exist_ok=True)
    
    # Construct command
    filepath = os.path.join("bin", "rhubarb")
    command = [
        filepath,
        "-f", "json",
        "-o", "static/lipsync.json",
        audio_path,
        "-r", "phonetic"
    ]
    
    # Run Rhubarb
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True
    )
    
    # Log success
    # logging.info(f"Lip sync generated successfully for {audio_path}")
    return True