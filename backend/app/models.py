"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    user_id: str = Field(default="default_user", description="User identifier")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    include_history: bool = Field(default=True, description="Include conversation history")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What's the weather like today?",
                "user_id": "user_123",
                "conversation_id": "conv_456",
                "include_history": True
            }
        }


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="Assistant response")
    user_id: str = Field(..., description="User identifier")
    conversation_id: str = Field(..., description="Conversation identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    tokens_used: Optional[int] = Field(None, description="Tokens used (if applicable)")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "The weather today is sunny with a high of 75°F.",
                "user_id": "user_123",
                "conversation_id": "conv_456",
                "timestamp": "2026-09-09T10:30:00",
                "tokens_used": 42,
                "processing_time_ms": 234.5
            }
        }


class VoiceInput(BaseModel):
    """Voice input model (for audio transcription)"""
    audio_file_path: str = Field(..., description="Path to audio file")
    user_id: str = Field(default="default_user", description="User identifier")
    language: str = Field(default="en", description="Language code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_file_path": "/uploads/audio_123.wav",
                "user_id": "user_123",
                "language": "en"
            }
        }


class VoiceOutput(BaseModel):
    """Voice output model (for text-to-speech)"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to speak")
    user_id: str = Field(default="default_user", description="User identifier")
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, this is Iris speaking.",
                "user_id": "user_123",
                "voice_speed": 1.0
            }
        }


class ConversationHistory(BaseModel):
    """Conversation history model"""
    conversation_id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
    messages: List[dict] = Field(default_factory=list, description="List of messages")
    created_at: datetime = Field(..., description="Conversation creation time")
    updated_at: datetime = Field(..., description="Last update time")
    message_count: int = Field(default=0, description="Total message count")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_456",
                "user_id": "user_123",
                "messages": [
                    {"role": "user", "content": "Hi Iris", "timestamp": "2026-09-09T10:00:00"},
                    {"role": "assistant", "content": "Hello! How can I help you?", "timestamp": "2026-09-09T10:00:05"}
                ],
                "created_at": "2026-09-09T10:00:00",
                "updated_at": "2026-09-09T10:00:05",
                "message_count": 2
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    detail: Optional[str] = Field(None, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid request",
                "error_code": "INVALID_INPUT",
                "detail": "Message cannot be empty",
                "timestamp": "2026-09-09T10:30:00"
            }
        }


class HealthCheck(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status (healthy/unhealthy)")
    version: str = Field(..., description="API version")
    llm_connected: bool = Field(..., description="LLM connection status")
    database_connected: bool = Field(..., description="Database connection status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "llm_connected": True,
                "database_connected": True,
                "timestamp": "2026-09-09T10:30:00"
            }
        }
