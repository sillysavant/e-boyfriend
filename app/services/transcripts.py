from fastapi import HTTPException, status
import uuid
from azure.cognitiveservices.speech import (
    SpeechConfig, 
    SpeechRecognizer, 
    AudioConfig, 
    ResultReason
)
import tempfile
from app.constant.config import AZURE_REGION_SERVICE, AZURE_SPEECH_KEY

async def transcript(audio_file: bytes):
    """
    Transcribes audio to text using Azure Speech SDK.

    Parameters:
        audio_file (bytes): The uploaded audio file in bytes.

    Returns:
        dict: Transcription result.
    """
    # Generate a unique identifier
    request_id = str(uuid.uuid4())
    
    # Check if audio file is empty
    if not audio_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No audio file provided."
        )

    # Write the audio bytes to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio_file:
        temp_audio_file.write(audio_file)
        temp_audio_file.flush()

        # Configure Azure Speech Recognition
        speech_config = SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION_SERVICE)
        speech_config.speech_recognition_language = "en-US"

        # Create an AudioConfig from the temp file
        audio_config = AudioConfig(filename=temp_audio_file.name)

        # Create a speech recognizer
        recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # Perform speech recognition
        result = recognizer.recognize_once()

        # Check recognition result
        if result.reason == ResultReason.RecognizedSpeech:
            transcription_text = result.text.strip()
            print(f"Transcription: {transcription_text}")

            # If transcription is empty, return a message
            if not transcription_text:
                return {
                    "sender": "",
                    "id": request_id,
                    "response": "No speech could be recognized."
                }

            return {
                "sender": transcription_text,
                "id": request_id,
                "response": transcription_text
            }
        elif result.reason == ResultReason.NoMatch:
            return {
                "sender": "",
                "id": request_id,
                "response": "No speech could be recognized."
            }
        else:
            error_details = f"Speech Recognition failed: {result.reason}"
            print(error_details)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_details
            )