import json
import os
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, status
from app.assistance.assistant import Assistant
from app.assistance.thread_manager import ThreadManager
from app.schema.conversation import ChatRequest
from app.services.transcripts import transcript
from app.services.tts import text_to_speech
from app.utils.wav_converter import convert_webm_to_wav
from app.utils.base64_converter import convert_audio_to_base64

router = APIRouter(tags=["conversation"])
# assistant 
assistant = Assistant()

@router.post("/chat")
def chat(
    request: Request,
    chat_request: ChatRequest
):
    # request process
    query = chat_request.text

    # thread 
    thread_manager = ThreadManager(request.session)
    thread_manager.create_thread()

    # add message to thread
    print(f"=== ADDING MESSAGE TO {thread_manager.thread.id} ===")
    thread_manager.add_message_to_thread(
        role="user", 
        content=f"Here are the list of all memory titles available: {assistant.list_memories()}"
    )
    print(f"assistant.list_memories(): {assistant.list_memories()}")
    thread_manager.add_message_to_thread(
        role="user", 
        content=f"Help your boyfriend with this query: {query}"
    )
    print(f"==== FINISHING ADDING MESSAGE ====")

    # run assistant
    response = thread_manager.run_assistant(
        assistant_id=Assistant.assistant_id
    )

    # Parse the chatbot response text
    response_detail = json.loads(response)
        
    # Convert chatbot text to speech
    text_to_speech(response_detail)

    audio_file = "/Users/longtv/Documents/Hackathon/eboyfriend-backend/static/output.wav"
    
    audio_base64=convert_audio_to_base64(audio_file)
    response_detail['audio'] = audio_base64

    # Return response with audio URL
    return response_detail 
    
        
@router.post("/wake")
async def detect_wake_word(
    audio: UploadFile = File(...)
):
    """
    Handles wake word detection by transcribing audio and generating a response.
    
    Parameters:
        audio_file (UploadFile): The audio file uploaded by the user.

    Returns:
        dict: Contains audio file URL and transcription text.
    """
    print("=== WAKE WORD DETECTION ===")
    # Read the audio file bytes
    audio_bytes = await audio.read()
    if audio.content_type == "audio/webm":
        print("Converting WEBM to WAV...")
        audio_bytes = convert_webm_to_wav(audio_bytes)
    elif audio.content_type != "audio/wav":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a WEBM or WAV file."
        )
    # Call transcript function to convert audio to text
    transcription_result = transcript(audio_bytes)

    if not transcription_result.get("response"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to transcribe audio."
        )
    
    transcripts = transcription_result["response"]
    print(f"transcription_result: {transcripts}")
    # Return transcription
    return {
        "transcribed_text": transcription_result["response"]
    }
    