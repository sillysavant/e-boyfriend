import json
import os
from app.constant.config import AZURE_REGION_SERVICE, AZURE_SPEECH_KEY
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig, ResultReason
from fastapi import HTTPException, status

def text_to_speech(response: dict):
    """
    Extracts the text from all messages and converts concatenated text to speech using Azure Speech SDK.

    Parameters:
        response (dict): The JSON response containing messages.
        output_file (str): The file to save the audio output.
    """
    # If response is a string, try to parse it
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            print("Could not parse response string to JSON")
            return

    # Extract messages from response
    messages = response.get("messages", [])
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get messages."
        )

    # Concatenate text from all messages
    text_to_speak = " ".join(message.get("text", "") for message in messages)

    if not text_to_speak.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text to convert."
        )

    # Define the static folder and file name
    static_folder = os.path.join(os.getcwd(), "static")
    os.makedirs(static_folder, exist_ok=True)  # Ensure the folder exists
    output_file = os.path.join(static_folder, "output.wav")

    speech_config = SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION_SERVICE)
    audio_config = AudioConfig(filename=output_file)  # Save audio to a file

    # Create Speech Synthesizer
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Convert text to speech
    # result = synthesizer.speak_text_async(text_to_speak).get()
    try:
        # Configure speech synthesis
        speech_config = SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION_SERVICE)
        
        # Optional: Customize voice (you can change the voice name)
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        
        # Configure audio output
        audio_config = AudioConfig(filename=output_file)

        # Create Speech Synthesizer
        synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # Perform speech synthesis
        result = synthesizer.speak_text_async(text_to_speak).get()

        # Detailed error checking
        if result.reason == ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized to [{output_file}]")
            return True
        elif result.reason == ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == ResultReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Speech synthesis error: {cancellation_details.error_details}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected speech synthesis result: {result.reason}"
            )

    except Exception as e:
        print(f"Unexpected error in text-to-speech: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}"
        )
