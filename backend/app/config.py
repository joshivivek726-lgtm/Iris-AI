"""
Configuration module for Iris AI
Handles environment variables and app settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    
    # App settings
    APP_NAME = "IRIS AI"
    APP_VERSION = "0.1.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server settings
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    
    # LLM settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # ollama, groq, openai
    LLM_MODEL = os.getenv("LLM_MODEL", "llama2")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", None)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
    
    # Voice settings
    STT_PROVIDER = os.getenv("STT_PROVIDER", "whisper")  # whisper, google
    TTS_PROVIDER = os.getenv("TTS_PROVIDER", "pyttsx3")  # pyttsx3, google, piper
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///iris.db")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./iris.db")
    
    # Memory settings
    MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", 10))
    ENABLE_MEMORY = os.getenv("ENABLE_MEMORY", "True").lower() == "true"
    
    # API settings
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", 120))
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", 5000))
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/iris.log")


# Create a single config instance
config = Config()


def get_config() -> Config:
    """Get application configuration"""
    return config


def print_config():
    """Print current configuration (for debugging)"""
    print("=" * 50)
    print("IRIS AI Configuration")
    print("=" * 50)
    print(f"App: {Config.APP_NAME} v{Config.APP_VERSION}")
    print(f"Debug: {Config.DEBUG}")
    print(f"LLM Provider: {Config.LLM_PROVIDER} ({Config.LLM_MODEL})")
    print(f"STT Provider: {Config.STT_PROVIDER}")
    print(f"TTS Provider: {Config.TTS_PROVIDER}")
    print(f"Database: {Config.DATABASE_PATH}")
    print(f"Memory Enabled: {Config.ENABLE_MEMORY}")
    print("=" * 50)
