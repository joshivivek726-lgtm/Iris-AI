# Iris AI - Free Tech Stack Guide

## 1. LLM CHOICE (Language Model)

### **Option A: Ollama + Llama 2 (BEST FOR PORTFOLIO) ⭐⭐⭐**
**Cost:** Free (open-source, runs locally)
**Pros:**
- Completely free, no API calls
- Runs on your Mac (no cloud dependency)
- Full control over model
- Great for demo (shows you understand LLMs)
- Can swap models easily (Llama 2, Mistral, etc.)

**Cons:**
- Slower than cloud APIs (but fine for demo)
- Requires ~8GB RAM for smooth operation

**Setup:**
```bash
# Install Ollama (macOS)
# Download from: https://ollama.ai

# Run Llama 2
ollama run llama2

# Then in Python:
import requests
response = requests.post('http://localhost:11434/api/generate', 
    json={"model": "llama2", "prompt": "Hello"})
```

---

### **Option B: Groq API (FREE TIER) ⭐⭐**
**Cost:** Free tier (thousands of requests/month)
**Pros:**
- Cloud-based, very fast
- Free tier is generous
- Easy setup (just API key)
- No local compute needed

**Cons:**
- Requires signup
- Rate limits on free tier
- Dependent on external service

**Setup:**
```bash
# Get free API key at: https://console.groq.com
pip install groq

# In code:
from groq import Groq
client = Groq(api_key="your_key")
```

---

### **Option C: Hugging Face (Transformers) ⭐**
**Cost:** Free (open-source)
**Pros:**
- Completely free
- Many models available
- Good for learning

**Cons:**
- Very slow on CPU
- Not ideal for real-time chat

---

## **RECOMMENDATION: START WITH OLLAMA**
- **Why:** Free, local, impressive for portfolio (shows you understand LLMs)
- **Fallback:** Groq API (if Ollama too slow for demo)

---

## 2. VOICE I/O (Speech-to-Text & Text-to-Speech)

### **Speech-to-Text (STT)**

#### **Option A: Whisper by OpenAI (FREE) ⭐⭐⭐**
**Cost:** Free (open-source, runs locally)
**Pros:**
- Best quality STT available
- Completely free, open-source
- Runs on your machine
- Very accurate

**Setup:**
```bash
pip install openai-whisper
# Download model (one-time):
whisper --model base

# In Python:
import whisper
model = whisper.load_model("base")
result = model.transcribe("audio.mp3")
print(result["text"])
```

---

#### **Option B: Google Cloud Speech-to-Text (FREE TIER)**
**Cost:** 60 minutes free per month
**Pros:** Very accurate, cloud-based
**Cons:** Limited free tier

---

### **Text-to-Speech (TTS)**

#### **Option A: pyttsx3 (FREE) ⭐⭐**
**Cost:** Free (open-source)
**Pros:**
- Completely free, offline
- Simple to use
- No API calls

**Cons:**
- Sound quality is lower (robotic)

**Setup:**
```bash
pip install pyttsx3

# In Python:
import pyttsx3
engine = pyttsx3.init()
engine.say("Hello, I'm Iris")
engine.runAndWait()
```

---

#### **Option B: Google Text-to-Speech (FREE TIER) ⭐⭐⭐**
**Cost:** Free tier (limited)
**Pros:** High-quality voices, sounds natural
**Cons:** Limited free tier (100 requests/month approx)

**Setup:**
```bash
pip install google-cloud-texttospeech
```

---

#### **Option C: Piper TTS (FREE) ⭐⭐**
**Cost:** Free (open-source)
**Pros:** Better quality than pyttsx3, completely free
**Cons:** Newer, less mature

**Setup:**
```bash
pip install piper-tts
```

---

## **RECOMMENDATION: STT + TTS COMBO**
- **STT:** Whisper (free, local, best quality)
- **TTS:** Piper or pyttsx3 (free, local) for MVP
- **Optional upgrade:** Google TTS if budget allows later

---

## 3. DATABASE

### **Option A: SQLite (BEST FOR PORTFOLIO) ⭐⭐⭐**
**Cost:** Free (built-in to Python)
**Pros:**
- Zero setup, built into Python
- Perfect for MVP/demo
- File-based (easy to backup)
- Sufficient for portfolio project
- Shows understanding of databases

**Cons:**
- Not suitable for massive scale (fine for portfolio)

**Setup:**
```bash
# No installation needed!
# Just use:
import sqlite3
conn = sqlite3.connect('iris.db')
```

---

### **Option B: PostgreSQL (LOCAL) ⭐⭐**
**Cost:** Free (open-source)
**Pros:**
- More professional than SQLite
- Better for complex queries
- Industry standard

**Cons:**
- Requires setup/installation
- Overkill for MVP

**Setup:**
```bash
brew install postgresql
brew services start postgresql
```

---

### **Option C: Supabase (FREE TIER) ⭐⭐**
**Cost:** Free tier
**Pros:**
- PostgreSQL in cloud
- Free tier is generous
- Easy setup

**Cons:**
- Requires signup
- External dependency

---

## **RECOMMENDATION: START WITH SQLITE**
- **Why:** Zero friction, built-in, perfect for MVP
- **Upgrade path:** Easy to migrate to PostgreSQL later if needed

---

## 4. CONVERSATION MEMORY & STORAGE

### **Option A: Vector Database (Embeddings) - WEAVIATE (FREE) ⭐⭐⭐**
**Cost:** Free (open-source)
**Pros:**
- Perfect for memory/context retrieval
- Semantic search (find relevant past conversations)
- Impressive for portfolio

**Setup:**
```bash
docker run -d -p 8080:8080 semitechnologies/weaviate:latest

pip install weaviate-client
```

---

### **Option B: Simple JSON/SQLite (MVP) ⭐⭐**
**Cost:** Free
**Pros:**
- Easiest to implement
- Good enough for MVP
- No extra dependencies

**Setup:**
```python
# Store conversations in SQLite as JSON
import json
import sqlite3

# Simple conversation log
```

---

## **RECOMMENDATION: START SIMPLE → UPGRADE LATER**
- **Phase 1 (MVP):** SQLite + JSON conversation logs
- **Phase 2 (Polish):** Add Weaviate for smart memory retrieval

---

## 5. CURRENT BLOCKERS - WHAT TO BUILD FIRST

### **MVP Phase (6 weeks) - BUILD THIS FIRST**
1. ✅ FastAPI backend (done)
2. ⏳ Chat endpoint (accept text input)
3. ⏳ LLM integration (Ollama)
4. ⏳ Conversation memory (SQLite)
5. ⏳ Simple tools (weather, web search)
6. ⏳ Voice input (Whisper)
7. ⏳ Voice output (pyttsx3)

### **Polish Phase (5 weeks)**
8. GUI frontend (simple web interface)
9. Documentation
10. Testing
11. Deployment prep

---

## COMPLETE FREE STACK (RECOMMENDED)

```
┌─────────────────────────────────────────────┐
│           Iris AI - Free Stack              │
├─────────────────────────────────────────────┤
│ LLM:           Ollama (Llama 2)             │
│ Backend:       FastAPI (done)               │
│ STT:           Whisper                      │
│ TTS:           pyttsx3 (later: Piper)       │
│ Database:      SQLite                       │
│ Memory:        SQLite + JSON (basic)        │
│ Tools:         Python requests, Selenium    │
│ Frontend:      FastAPI + simple HTML/JS     │
│ Deployment:    GitHub Pages / Heroku free   │
└─────────────────────────────────────────────┘
```

**Total Cost: $0** ✅

---

## INSTALLATION ROADMAP

### **Phase 1: Core Setup (This Week)**
```bash
# 1. Install Ollama
# 2. Install dependencies
pip install ollama openai-whisper pyttsx3 python-dotenv requests

# 3. Set up SQLite (no install needed)
# 4. Create simple chat endpoint
# 5. Test with local LLM
```

### **Phase 2: Voice (Next Week)**
```bash
# Add Whisper STT
# Add pyttsx3 TTS
# Connect to chat endpoint
```

### **Phase 3: Tools & Memory (Week 3-4)**
```bash
# Add weather tool
# Add web search
# Store conversations in SQLite
```

### **Phase 4: Polish & Launch (Week 5-6)**
```bash
# Add simple GUI
# Write documentation
# Deploy to GitHub
```

---

## ALTERNATIVE: Hybrid Free Approach

If you want **cloud backup** without paying:

| Component | Free Option | Tier Limit |
|-----------|------------|-----------|
| LLM | Groq API | 30 req/min |
| STT | Whisper (local) | Unlimited |
| TTS | pyttsx3 (local) | Unlimited |
| Database | Supabase | 500MB, 50k rows |
| Storage | GitHub (free) | Unlimited |

---

## NEXT STEPS

1. **Install Ollama now** (download from ollama.ai)
2. **Run Llama 2** (`ollama run llama2`)
3. **Test Whisper** (`pip install openai-whisper`)
4. **Set up SQLite** (built-in to Python)
5. **Share your current `main.py`** → I'll integrate these

**Ready to build?** 🚀
