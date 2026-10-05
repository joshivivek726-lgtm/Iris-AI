# Iris AI

A Jarvis-inspired voice assistant that runs entirely on your own machine. It uses free, open-source tools, with no cloud APIs and no API keys.

Speak to Iris, and it transcribes your voice, thinks with a local LLM, uses tools for real-time information, and answers out loud.

## Features

- **Local LLM**: Llama 3.2 (3B) served by Ollama
- **Voice input**: OpenAI Whisper speech-to-text, running locally
- **Voice output**: native macOS speech synthesis
- **Conversation memory**: multi-turn context stored in SQLite
- **Tools**: current date and time, live weather (Open-Meteo), news search (Google News RSS)
- **REST API**: FastAPI with auto-generated docs at `/docs`
- **Tests**: pytest suite covering the API and tools

## Architecture

```
Audio file --> Whisper (STT) --> FastAPI --> Tool router --> Ollama (Llama 3.2) --> macOS TTS
                                    |
                                 SQLite (conversation memory)
```

## Setup

Requirements: macOS, Python 3.8+, [Ollama](https://ollama.com), ffmpeg (`brew install ffmpeg`)

```bash
git clone <your-repo-url>
cd Iris-AI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
ollama pull llama3.2:3b
uvicorn backend.app.main:app --reload --reload-dir backend
```

Interactive API docs: http://localhost:8000/docs

## Usage

```bash
# Text chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Tampa?", "user_id": "me"}'

# Voice chat (audio in, spoken reply out)
curl -X POST http://localhost:8000/api/voice-chat -F "file=@question.m4a"
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/chat` | Text chat with memory |
| POST | `/api/voice-chat` | Audio in, Whisper, LLM, spoken reply |
| POST | `/api/transcribe` | Speech-to-text only |
| POST | `/api/speak` | Text-to-speech only |
| GET | `/api/conversations/{id}` | Conversation history |

## Tests

```bash
python3 -m pytest tests -v
```

## Known limitations

- Voice output uses the macOS `say` command, so speech is macOS-only
- The SQLite connection is shared across threads (`check_same_thread=False`), which is fine for one user but needs a lock or per-request connections for concurrent use
- Tool routing uses keyword matching, since small local models are unreliable at choosing tools themselves
- Built for an 8 GB machine, so replies take a few seconds and voice chat 15 to 30 seconds

## Roadmap

- Faster voice replies (shorter spoken answers, non-blocking speech)
- Web frontend
- Semantic memory with embeddings