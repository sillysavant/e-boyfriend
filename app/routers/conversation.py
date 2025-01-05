import json
from typing import Literal
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status, BackgroundTasks
from app.assistance.agents import IntentClassifier, Reformulate_agent, Relationship_Consulting_agent, UserProxy, get_intent_classifier, get_reformulate_agent, get_relationship_consulting_agent, get_user_proxy
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, status
from app.assistance.conversation_agent import Conversation_Agent, get_conversation_agent
from app.assistance.documents_reading_agent import DocumentReadingAgent, get_document_reading_agent
from app.assistance.scrape_agent import WebSearchAgent, get_web_scaper_agent
from app.assistance.thread_manager import ThreadManager
from app.database.database import get_db, run_with_session
from app.database.query import db_message
from app.schema.conversation import ChatRequest
from app.services.azure_docs_intel_service import upload_docs
from app.services.transcripts import transcript
from app.services.tts import text_to_speech
from app.utils.azure_blob_helper import AzureBlobHelper
from app.utils.lipsync import generate_lip_sync
from app.utils.read_json import read_json_file
from app.utils.wav_converter import convert_webm_to_wav
from app.utils.base64_converter import convert_audio_to_base64
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import conversation_service

router = APIRouter(tags=["conversation"])
        
@router.post("/chat")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    background_task: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_proxy: UserProxy = Depends(get_user_proxy),
    relationship_consulting: Relationship_Consulting_agent = Depends(get_relationship_consulting_agent),
    reformulate_agent: Reformulate_agent = Depends(get_reformulate_agent),
    conversation_agent: Conversation_Agent = Depends(get_conversation_agent),
    web_search_agent: WebSearchAgent = Depends(get_web_scaper_agent),
    intent_classifier: IntentClassifier = Depends(get_intent_classifier),
    document_reading_agent: DocumentReadingAgent = Depends(get_document_reading_agent)
):
    try: 
        query = chat_request.text
        # thread 
        thread_manager = ThreadManager(request.session)
        await thread_manager.create_thread()
        session_id = thread_manager.thread.id
        
        # request process
        response = await conversation_service.chat(
            db = db, 
            message=query, 
            session_id=session_id,
            user_proxy=user_proxy,
            relationship_consulting=relationship_consulting,
            reformulate_agent=reformulate_agent,
            conversation_agent=conversation_agent,
            web_search_agent = web_search_agent,
            intent_classifier = intent_classifier,
            document_reading_agent = document_reading_agent
        )

        # Parse the chatbot response text
        response_detail = json.loads(response[-1].chat_history[-1]['content'])
        
        # Generate audio for each message
        try:
            response_json = response_detail["messages"]
        except KeyError:
            response_json = response_detail["responses"]
        except KeyError:
            response_json = response_detail["response"]
        for message in response_json:
            # Convert individual message text to speech
            await text_to_speech({"messages": [message]})
            
            audio_file = "static/output.wav"

            # Generate lipsync data
            await generate_lip_sync(audio_file)

            # Attach audio and lipsync data to message
            message["audio"] = convert_audio_to_base64(audio_file)
            message["lipsync"] = read_json_file("static/lipsync.json")
        
        # BACKGROUND TASK: add user's message , assistant message to database
        background_task.add_task(run_with_session, conversation_service.add_user_message, session_id, query)
        background_task.add_task(run_with_session, conversation_service.add_assistant_message, session_id, response)
        # BACKGROUND: reset the agents
        background_task.add_task(conversation_service.reset_agent, [user_proxy, relationship_consulting, reformulate_agent, conversation_agent, web_search_agent, intent_classifier])
        
        return response_json
    except Exception as e:
        print(f"Error in conversation.py: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/wake")
async def detect_wake_word(
    audio: UploadFile = File(...)
):
    # Read the audio file bytes
    audio_bytes = await audio.read()
    if audio.content_type == "audio/webm":
        audio_bytes = convert_webm_to_wav(audio_bytes)
    elif audio.content_type != "audio/wav":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a WEBM or WAV file."
        )
    # Call transcript function to convert audio to text
    transcription_result = await transcript(audio_bytes)

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
    
@router.post("/test")
async def add_db_test(
    request: Request,
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    try: 
        query = chat_request.text
        # thread 
        thread_manager = ThreadManager(request.session)
        await thread_manager.create_thread()
        session_id = thread_manager.thread.id
        print(f"session_id: {session_id}") 
        new_messages = await db_message.add_messages(db=db, session_id=session_id, role="user", content=query)
        return {
            "session_id": new_messages.session_id,
            "role": new_messages.role,
            "content": new_messages.content
        }
    except Exception as e:
        print(f"Error in conversation.py: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= e
        )       
        
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    index_name: Literal["user_docs", "user_info"] = Form(...)
):
    if file.content_type != 'application/pdf':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a PDF file."
        )
    
    await upload_docs(uploaded_file=file, category="uploaded_docs", index_name=index_name)
    
    return {"detail": "File uploaded successfully"}
