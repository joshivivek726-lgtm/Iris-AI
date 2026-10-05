"""
Routes for Iris AI chat functionality
Handles chat requests, LLM integration, and conversation management
"""

import logging
import requests
import time
import uuid
import os
import tempfile
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional

from backend.app.config import config
from backend.app.models import ChatRequest, ChatResponse, ConversationHistory, ErrorResponse
from backend.app.database import get_database

from fastapi import UploadFile, File
from backend.app.voice_service import transcribe_file
from pydantic import BaseModel
from backend.app.tts_service import speak
from backend.app.tools import run_tools

logger = logging.getLogger(__name__)

router = APIRouter()


class LLMService:
    """Service for LLM interactions"""
    
    @staticmethod
    def call_ollama(messages: list, model: str = None) -> str:
        """Call Ollama chat API"""
        if model is None:
            model = config.LLM_MODEL
        try:
            logger.info(f"Calling Ollama with model: {model}")
            response = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "keep_alive": "30m",
                    "options": {"num_ctx": 2048, "num_predict": 200}
                },
                timeout=config.API_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "").strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise HTTPException(status_code=503, detail="LLM service unavailable")
    
    @staticmethod
    def call_groq(prompt: str) -> str:
        """Call Groq API (if available)"""
        if not config.GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="Groq API key not configured")
        
        try:
            from groq import Groq
            client = Groq(api_key=config.GROQ_API_KEY)
            message = client.messages.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise HTTPException(status_code=503, detail="LLM service unavailable")
    
    @staticmethod
    def generate_response(prompt: str, history: Optional[list] = None) -> str:
        """Generate response using configured LLM"""
        if config.LLM_PROVIDER == "ollama":
            system = "You are Iris, a helpful, concise AI assistant. Answer directly in plain text."
            tool_result = run_tools(prompt)
            if tool_result:
                system += f"\n\nUse this real-time information to answer: {tool_result}"
            messages = [{"role": "system", "content": system}]
            messages += history or []
            messages.append({"role": "user", "content": prompt})
            return LLMService.call_ollama(messages)
        elif config.LLM_PROVIDER == "groq":
            return LLMService.call_groq(prompt)
        else:
            raise HTTPException(status_code=500, detail="LLM provider not configured")    


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint
    
    - **message**: User message (required)
    - **user_id**: User identifier (optional, defaults to "default_user")
    - **conversation_id**: Existing conversation (optional, creates new if not provided)
    - **include_history**: Include conversation history in context (optional, defaults to True)
    """
    start_time = time.time()
    
    try:
        # Validate input
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(request.message) > config.MAX_MESSAGE_LENGTH:
            raise HTTPException(status_code=400, detail=f"Message too long (max {config.MAX_MESSAGE_LENGTH} chars)")
        
        logger.info(f"Chat request from {request.user_id}: {request.message[:50]}...")
        
        # Get or create conversation
        db = get_database()
        if request.conversation_id:
            conversation_id = request.conversation_id
            cursor = db.connection.cursor()
            cursor.execute(
                "SELECT 1 FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
            db.create_conversation(conversation_id, request.user_id)
            logger.info(f"Created new conversation: {conversation_id}")

        # Save user message
        db.save_message(conversation_id, request.user_id, "user", request.message)
        
        # Build history as chat messages
        history_msgs = []
        if request.include_history and config.ENABLE_MEMORY:
            history = db.get_conversation_history(conversation_id, config.MAX_CONVERSATION_HISTORY)
            history_msgs = [{"role": m["role"], "content": m["content"]} for m in history[:-1]]
        
                # Generate response using LLM
        try:
            response_text = LLMService.generate_response(request.message, history_msgs)
        except HTTPException as e:
            logger.error(f"LLM error: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during LLM call: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate response")
        
        # Save assistant response
        processing_time_ms = (time.time() - start_time) * 1000
        db.save_message(conversation_id, request.user_id, "assistant", response_text)
        
        # Create response
        chat_response = ChatResponse(
            response=response_text,
            user_id=request.user_id,
            conversation_id=conversation_id,
            processing_time_ms=processing_time_ms
        )
        
        logger.info(f"Chat response generated in {processing_time_ms:.2f}ms")
        return chat_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/conversations/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(conversation_id: str, limit: int = Query(10, ge=1, le=100)):
    """
    Get conversation history
    
    - **conversation_id**: Conversation ID (required)
    - **limit**: Maximum number of messages to return (optional, default 10)
    """
    try:
        db = get_database()
        messages = db.get_conversation_history(conversation_id, limit)
        
        if not messages:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get conversation metadata
        cursor = db.connection.cursor()
        cursor.execute('''
            SELECT conversation_id, user_id, created_at, updated_at, message_count
            FROM conversations WHERE conversation_id = ?
        ''', (conversation_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationHistory(
            conversation_id=row[0],
            user_id=row[1],
            messages=[dict(m) for m in messages],
            created_at=datetime.fromisoformat(row[2]),
            updated_at=datetime.fromisoformat(row[3]),
            message_count=row[4]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")


@router.get("/users/{user_id}/conversations")
async def get_user_conversations(user_id: str, limit: int = Query(5, ge=1, le=50)):
    """
    Get recent conversations for a user
    
    - **user_id**: User ID (required)
    - **limit**: Maximum number of conversations to return (optional, default 5)
    """
    try:
        db = get_database()
        conversations = db.get_recent_conversations(user_id, limit)
        
        return {
            "user_id": user_id,
            "conversations": conversations,
            "count": len(conversations)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversations")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation
    
    - **conversation_id**: Conversation ID (required)
    """
    try:
        db = get_database()
        success = db.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": f"Conversation {conversation_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


@router.post("/preferences/{user_id}")
async def set_user_preferences(user_id: str, preferences: dict):
    """
    Set user preferences
    
    - **user_id**: User ID (required)
    - **preferences**: Preferences dictionary (required)
    """
    try:
        db = get_database()
        success = db.save_user_preference(user_id, preferences)
        
        return {
            "user_id": user_id,
            "message": "Preferences saved",
            "preferences": preferences
        }
        
    except Exception as e:
        logger.error(f"Error saving preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to save preferences")


@router.get("/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """
    Get user preferences
    
    - **user_id**: User ID (required)
    """
    try:
        db = get_database()
        preferences = db.get_user_preference(user_id)
        
        return {
            "user_id": user_id,
            "preferences": preferences or {}
        }
        
    except Exception as e:
        logger.error(f"Error retrieving preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve preferences")

@router.post("/transcribe")
def transcribe_endpoint(file: UploadFile = File(...)):
    """Transcribe an uploaded audio file to text"""
    suffix = os.path.splitext(file.filename or "")[1] or ".m4a"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        text = transcribe_file(tmp_path)
        logger.info(f"Transcribed audio: {text[:50]}")
        return {"text": text}
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Transcription failed")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


class SpeakRequest(BaseModel):
    text: str


@router.post("/speak")
def speak_endpoint(request: SpeakRequest):
    """Speak text aloud using the Mac's built-in voice"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(request.text) > 1000:
        raise HTTPException(status_code=400, detail="Text too long (max 1000 chars)")
    try:
        speak(request.text)
        return {"status": "spoken"}
    except Exception as e:
        logger.error(f"Speak error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Speech failed")
    

@router.post("/voice-chat")
def voice_chat_endpoint(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    conversation_id: Optional[str] = None,
):
    """Audio in -> Whisper -> LLM -> spoken reply"""
    start_time = time.time()
    suffix = os.path.splitext(file.filename or "")[1] or ".m4a"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        text = transcribe_file(tmp_path)
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Transcription failed")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    if not text:
        raise HTTPException(status_code=400, detail="No speech detected")

    db = get_database()
    if conversation_id:
        cursor = db.connection.cursor()
        cursor.execute(
            "SELECT 1 FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        db.create_conversation(conversation_id, user_id)

    db.save_message(conversation_id, user_id, "user", text)
    history = db.get_conversation_history(conversation_id, config.MAX_CONVERSATION_HISTORY)
    history_msgs = [{"role": m["role"], "content": m["content"]} for m in history[:-1]]

    response_text = LLMService.generate_response(text, history_msgs)
    db.save_message(conversation_id, user_id, "assistant", response_text)

    try:
        speak(response_text)
    except Exception as e:
        logger.error(f"Speak error: {e}")

    return {
        "transcript": text,
        "response": response_text,
        "conversation_id": conversation_id,
        "processing_time_ms": (time.time() - start_time) * 1000,
    }
