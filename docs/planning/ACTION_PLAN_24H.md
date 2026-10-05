# Iris AI - 24-Hour Action Plan

**Current Status:** Foundation skeleton ready (20% complete)  
**Target:** Production-ready foundation (100% complete) in 24 hours  
**Time Investment:** 2-3 hours of focused work

---

## WHAT YOU'RE GETTING

I've created **complete, production-ready code** that:
- ✅ Integrates Ollama LLM (free, local, no API key needed)
- ✅ Sets up SQLite database (persistent conversation storage)
- ✅ Adds structured error handling
- ✅ Implements conversation memory
- ✅ Creates comprehensive API documentation
- ✅ Provides health checks and monitoring
- ✅ Follows all Python/FastAPI best practices

**Files created for you:**
1. `requirements.txt` - All dependencies
2. `config.py` - Centralized configuration
3. `models.py` - Pydantic validation models
4. `database.py` - SQLite setup & operations
5. `main_refactored.py` - Production FastAPI app
6. `routes_refactored.py` - Chat with LLM integration
7. `FOUNDATION_AUDIT.md` - Detailed gap analysis
8. `IMPLEMENTATION_GUIDE.md` - Step-by-step setup
9. `PHASE_1_ROADMAP.md` - 6-week MVP plan
10. `iris_free_tech_stack.md` - Free alternatives guide

---

## NEXT 24 HOURS: STEP-BY-STEP

### HOUR 1: Download & Install Ollama (10-15 min)

**Why:** Ollama is your AI engine (free, runs locally, no API key)

1. Visit: https://ollama.ai
2. Download for macOS
3. Install & run
4. Let it download Llama 2 model (~4GB, takes 10-15 min)

```bash
# After installation, run in terminal
ollama run llama2

# Keep this terminal open! It stays running in background
```

**What you should see:**
```
>>> (waiting for input)
>>> send a message (/help for help)
```

✅ **Success:** Ollama running and ready

---

### HOUR 2: Copy Files to Your Project (10 min)

**These are the refactored files I created:**

```bash
cd ~/Desktop/Iris-AI

# Copy configuration files
cp ~/claude_outputs/config.py ./
cp ~/claude_outputs/models.py ./
cp ~/claude_outputs/database.py ./

# Copy production-ready main.py
cp ~/claude_outputs/main_refactored.py backend/app/main.py

# Copy routes with LLM integration
cp ~/claude_outputs/routes_refactored.py backend/app/routes.py

# Copy dependencies
cp ~/claude_outputs/requirements.txt ./

# Create logs directory
mkdir -p logs
```

**What you should see:**
```
Iris-AI/
├── config.py           ✅ NEW
├── models.py           ✅ NEW
├── database.py         ✅ NEW
├── requirements.txt    ✅ UPDATED
├── .env                ✅ EXISTING
├── backend/
│   ├── __init__.py     (create if missing)
│   └── app/
│       ├── __init__.py (create if missing)
│       ├── main.py     ✅ REPLACED
│       └── routes.py   ✅ REPLACED
├── logs/               ✅ NEW (directory)
└── venv/
```

✅ **Success:** All files in place

---

### HOUR 3: Install Dependencies (10 min)

```bash
cd ~/Desktop/Iris-AI
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# This installs:
# - FastAPI, Uvicorn (already had)
# - Pydantic (already had)
# - requests, httpx (new - for API calls)
# - whisper, pyttsx3 (new - for voice)
# - pytest (for testing)
```

**Expected output at end:**
```
Successfully installed [list of packages]
```

✅ **Success:** Dependencies installed

---

### HOUR 4: Update Configuration (5 min)

Edit `.env` file with these settings:

```bash
# Mac command to open .env in editor
nano .env
```

Add/update these lines:

```env
# App
DEBUG=False
HOST=127.0.0.1
PORT=8000

# LLM (Ollama)
LLM_PROVIDER=ollama
LLM_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434

# Database
DATABASE_PATH=./iris.db
ENABLE_MEMORY=True
MAX_CONVERSATION_HISTORY=10

# Other
LOG_LEVEL=INFO
LOG_FILE=./logs/iris.log
```

**Save & exit:** Press `Ctrl+X`, then `Y`, then `Enter`

✅ **Success:** Configuration updated

---

### HOUR 5: Test Everything (20 min)

**In Terminal 1 (Ollama - KEEP RUNNING):**
```bash
ollama run llama2
```

**In Terminal 2 (FastAPI Server):**
```bash
cd ~/Desktop/Iris-AI
source venv/bin/activate
uvicorn backend.app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Database initialized successfully
```

**In Terminal 3 (Test requests):**

Test 1: Health Check
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "llm_connected": true,
  "database_connected": true,
  "timestamp": "2026-09-09T..."
}
```

Test 2: Chat with AI
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what is your name?",
    "user_id": "test_user"
  }'
```

**Expected response:**
```json
{
  "response": "Hello! I'm Iris, an AI assistant created to help you...",
  "user_id": "test_user",
  "conversation_id": "conv_abc123def456",
  "timestamp": "2026-09-09T...",
  "processing_time_ms": 1234.5
}
```

Test 3: API Documentation
```
Visit: http://localhost:8000/docs
```

**Expected:** Interactive API documentation with all endpoints

✅ **Success:** Everything working!

---

## IF YOU HIT ERRORS

### Error: "ModuleNotFoundError"
```bash
# Make sure __init__.py exists
touch backend/__init__.py
touch backend/app/__init__.py

# Restart server
```

### Error: "Ollama connection refused"
```bash
# Make sure Ollama is running in another terminal
ollama run llama2

# Or test it
curl http://localhost:11434/api/tags
```

### Error: "Database error"
```bash
# Delete old database and restart
rm iris.db

# Logs will help debug
tail -f logs/iris.log
```

### Error: "Chat returns empty"
```bash
# Check Ollama is responding
curl http://localhost:11434/api/tags

# Check full logs
cat logs/iris.log
```

---

## WHAT YOU NOW HAVE

After 24 hours, your foundation will be:

### ✅ Functional
- Chat endpoint accepting text
- LLM integration (Ollama Llama 2)
- Conversation storage (SQLite)
- Health monitoring
- Error handling
- Logging

### ✅ Professional
- Production-ready code
- Proper project structure
- Configuration management
- API documentation (auto-generated)
- Database schema
- Error responses

### ✅ Extensible
- Easy to add voice I/O
- Easy to add tools
- Easy to add more LLMs
- Easy to add testing
- Easy to deploy

---

## NEXT 7 DAYS (AFTER TODAY)

Once foundation is solid:

### Day 2-3: Voice I/O
- Install Whisper (speech-to-text)
- Create voice endpoint
- Install pyttsx3 (text-to-speech)
- Test voice chat

### Day 4-5: Memory & Tools
- Test conversation history
- Add weather tool
- Add web search tool
- Test tool integration

### Day 6-7: Polish & Testing
- Write unit tests
- Update documentation
- Create demo
- Prepare GitHub

**Full Phase 1 roadmap:** See `PHASE_1_ROADMAP.md`

---

## RECOMMENDED WORKFLOW

1. **Read first:** `FOUNDATION_AUDIT.md` (10 min) - understand gaps
2. **Setup:** `IMPLEMENTATION_GUIDE.md` (step-by-step)
3. **Execute:** Follow this 24-hour plan
4. **Plan ahead:** `PHASE_1_ROADMAP.md` (detailed weeks 1-6)
5. **Reference:** `iris_free_tech_stack.md` (alternatives)

---

## SUCCESS CHECKLIST

By end of today, you should have:

- [ ] Ollama downloaded and running
- [ ] All files copied to project
- [ ] Dependencies installed (pip)
- [ ] .env configured
- [ ] FastAPI server starts without errors
- [ ] Health endpoint returns 200
- [ ] Chat endpoint returns response from Llama 2
- [ ] Database file created (iris.db)
- [ ] Logs directory functional
- [ ] API docs visible at /docs

**When all checkboxes are ✅, you're ready for Phase 1B (database & memory)!**

---

## QUICK REFERENCE COMMANDS

```bash
# Activate virtual environment
source venv/bin/activate

# Start Ollama (Terminal 1)
ollama run llama2

# Start FastAPI server (Terminal 2)
uvicorn backend.app.main:app --reload

# Test health (Terminal 3)
curl http://localhost:8000/health

# Test chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": "test"}'

# View logs
tail -f logs/iris.log

# View API docs
# Open browser to: http://localhost:8000/docs

# Install new dependency
pip install package_name

# Format code
black backend/

# Check code quality
flake8 backend/
```

---

## YOU'VE GOT THIS! 🚀

**Timeline:** 2-3 focused hours today  
**Result:** Production-ready AI assistant foundation  
**Next:** 5 more weeks to full MVP

**Key mindset:**
- ✅ Focus on quality, not features
- ✅ Test each step as you go
- ✅ Refer to documentation if stuck
- ✅ One week at a time

**Questions?** Check:
1. Error message logs
2. IMPLEMENTATION_GUIDE.md
3. FOUNDATION_AUDIT.md (for what each file does)
4. Ask me for help!

---

## JUST START

Right now:
1. Open Terminal
2. Download Ollama from https://ollama.ai
3. Run `ollama run llama2`
4. Copy files to your project
5. Run server
6. Test endpoints

**That's it! You've got everything you need. Let's build Iris AI! 🚀**

---

**Progress tracker:**
- [ ] Hour 1: Ollama installed
- [ ] Hour 2: Files copied
- [ ] Hour 3: Dependencies installed
- [ ] Hour 4: Configuration done
- [ ] Hour 5: Tests passing

**Come back when you've completed these steps and let me know how it went!**
