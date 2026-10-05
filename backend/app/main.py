"""
Iris AI - FastAPI Application
Main entry point for the Iris AI assistant
"""

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

# Import configuration and database
from backend.app.config import config, get_config, print_config
from backend.app.database import init_database, get_database
from backend.app.models import ErrorResponse, HealthCheck

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.LOG_FILE, mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    description="Jarvis-inspired AI Assistant",
    version=config.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    logger.info("=" * 50)
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    logger.info("=" * 50)
    
    # Print configuration
    print_config()
    
    # Initialize database
    try:
        db = init_database(config.DATABASE_PATH)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    logger.info(f"App started at {datetime.utcnow()}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {config.APP_NAME}")
    try:
        db = get_database()
        db.disconnect()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_response = ErrorResponse(
        error="Internal Server Error",
        error_code="INTERNAL_ERROR",
        detail=str(exc) if config.DEBUG else "An unexpected error occurred"
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        db = get_database()
        db_connected = db.connection is not None
    except:
        db_connected = False
    
    # Check LLM connection (basic ping)
    llm_connected = False
    if config.LLM_PROVIDER == "ollama":
        try:
            import requests
            response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=2)
            llm_connected = response.status_code == 200
        except:
            llm_connected = False
    
    status = "healthy" if (db_connected and llm_connected) else "degraded"
    
    return HealthCheck(
        status=status,
        version=config.APP_VERSION,
        llm_connected=llm_connected,
        database_connected=db_connected
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "chat": "/chat"
    }


# Import and include routers
try:
    from backend.app.routes import router as chat_router
    app.include_router(chat_router, prefix="/api", tags=["chat"])
    logger.info("Chat router loaded successfully")
except ImportError as e:
    logger.warning(f"Could not import chat router: {e}")


# Additional info
@app.get("/api/info")
async def info():
    """Get API information"""
    try:
        db = get_database()
        stats = db.get_db_stats()
    except:
        stats = {"error": "Could not fetch statistics"}
    
    return {
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "description": "Jarvis-inspired AI Assistant",
        "llm": {
            "provider": config.LLM_PROVIDER,
            "model": config.LLM_MODEL
        },
        "voice": {
            "stt": config.STT_PROVIDER,
            "tts": config.TTS_PROVIDER
        },
        "database": {
            "path": config.DATABASE_PATH,
            "stats": stats
        },
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server at {config.HOST}:{config.PORT}")
    uvicorn.run(
        "main_refactored:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )
