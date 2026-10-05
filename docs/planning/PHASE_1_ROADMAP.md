# Iris AI - Phase 1 MVP Roadmap

**Duration:** 6 weeks (Sept 10 - Oct 20, 2026)  
**Goal:** Fully functional AI assistant with voice I/O and memory  
**Target:** Stable, testable MVP ready for GitHub release

---

## PHASE 1A: Critical Foundation (Week 1)
**Timeline:** Sept 10-14  
**Goal:** Production-ready backend foundation

### Day 1-2: Integration & Setup (Sept 10-11)
- [ ] Copy all refactored files to project
- [ ] Update requirements.txt and install deps
- [ ] Copy config.py, models.py, database.py
- [ ] Update .env configuration
- [ ] Create logs/ directory
- [ ] Test basic startup (no errors)

**Checklist:**
```bash
# Complete these steps
pip install -r requirements.txt
cp config.py backend/
cp models.py backend/
cp database.py backend/
cp main_refactored.py backend/app/main.py
cp routes_refactored.py backend/app/routes.py
mkdir -p logs
```

**Tests:**
- [ ] `uvicorn backend.app.main:app --reload` starts without errors
- [ ] `curl http://localhost:8000/` returns API info
- [ ] `curl http://localhost:8000/health` returns healthy status
- [ ] Database creates `iris.db` on first run
- [ ] Logs directory is writable

### Day 3-4: Ollama Integration & Testing (Sept 12-13)
- [ ] Download and install Ollama (https://ollama.ai)
- [ ] Run `ollama run llama2` and verify download
- [ ] Test Ollama endpoint: `curl http://localhost:11434/api/tags`
- [ ] Update .env with correct OLLAMA_BASE_URL
- [ ] Test chat endpoint with simple message
- [ ] Verify response from Llama 2

**Checklist:**
```bash
# Install Ollama and test
ollama run llama2

# In another terminal, test API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Say hello", "user_id": "test"}'
```

**Tests:**
- [ ] Ollama responds to API calls
- [ ] Chat endpoint returns valid response
- [ ] Response is from Llama 2 (not hardcoded)
- [ ] Processing time is reasonable (<10s)
- [ ] Error handling works (bad requests return proper errors)

### Day 5: Documentation & Testing (Sept 14)
- [ ] Write setup instructions in README.md
- [ ] Document all endpoints in API_DOCS.md
- [ ] Create example curl commands
- [ ] Test with Postman/curl collection
- [ ] Write project architecture diagram

**Tests:**
- [ ] All endpoints documented
- [ ] Example requests/responses provided
- [ ] API docs auto-generate at /docs
- [ ] README has setup instructions
- [ ] Code follows PEP 8 (run `black` formatter)

### Deliverables (End of Week 1)
- ✅ Production-ready FastAPI app
- ✅ Ollama LLM integration working
- ✅ SQLite database initialized
- ✅ Basic API documentation
- ✅ Working chat endpoint
- ✅ Health check endpoint

---

## PHASE 1B: Database & Memory (Week 2)
**Timeline:** Sept 17-21  
**Goal:** Persistent conversation storage and retrieval

### Day 1-2: Conversation Storage (Sept 17-18)
- [ ] Test conversation creation
- [ ] Test message saving
- [ ] Test conversation history retrieval
- [ ] Test multiple conversations per user
- [ ] Verify database schema

**Tests:**
```bash
# Test creating conversation and saving messages
# Test retrieving history
curl http://localhost:8000/api/conversations/{id}

# Test multi-turn conversation
# Message 1: "What's your name?"
# Message 2: "What can you do?"
# Message 3: "Tell me a joke"
# Verify all messages saved and retrieved correctly
```

**Checklist:**
- [ ] Conversations table working
- [ ] Messages table working
- [ ] User preferences table working
- [ ] Message history retrieval working
- [ ] Database indexes created
- [ ] Query performance acceptable

### Day 3-4: Memory & Context (Sept 19-20)
- [ ] Implement conversation context in chat
- [ ] Test history-aware responses
- [ ] Test conversation continuation
- [ ] Test context limit (MAX_CONVERSATION_HISTORY)
- [ ] Implement conversation summary (for long chats)

**Tests:**
```bash
# Multi-turn conversation
# 1. "My name is John"
# 2. "What's my name?" (should remember)
# 3. "I like pizza" 
# 4. "What's my favorite food?" (should remember)
```

**Checklist:**
- [ ] Context passed to LLM correctly
- [ ] History limited to MAX_CONVERSATION_HISTORY
- [ ] Old conversations archived (not deleted)
- [ ] Memory retrieval is fast
- [ ] Context formatting is clean

### Day 5: User Profiles & Preferences (Sept 21)
- [ ] Implement user preferences storage
- [ ] Test preference persistence
- [ ] Test preference retrieval
- [ ] Test preference updates
- [ ] Add preference validation

**Tests:**
```bash
# Set preferences
curl -X POST http://localhost:8000/api/preferences/john \
  -H "Content-Type: application/json" \
  -d '{"favorite_color": "blue", "timezone": "EST"}'

# Get preferences
curl http://localhost:8000/api/preferences/john
```

**Checklist:**
- [ ] Preferences save correctly
- [ ] Preferences retrieve correctly
- [ ] Updates overwrite previous values
- [ ] Preferences are JSON-compatible
- [ ] Edge cases handled

### Deliverables (End of Week 2)
- ✅ Conversation history working
- ✅ Multi-turn conversations working
- ✅ Context-aware responses
- ✅ User preferences system
- ✅ Database fully tested
- ✅ Memory layer functional

---

## PHASE 1C: Voice I/O - STT (Week 3a)
**Timeline:** Sept 24-26  
**Goal:** Speech-to-text transcription

### Day 1-2: Whisper Setup (Sept 24-25)
- [ ] Install openai-whisper
- [ ] Download base model
- [ ] Create audio endpoint
- [ ] Test with sample audio file

```bash
pip install openai-whisper
# Download model (one-time)
whisper --model base --download-root ~/.cache/whisper
```

**Checklist:**
- [ ] Whisper installed
- [ ] Model downloaded
- [ ] Test audio file working
- [ ] Basic transcription working

### Day 3: Voice Endpoint (Sept 26)
- [ ] Create `/api/voice/transcribe` endpoint
- [ ] Accept audio file upload
- [ ] Return text transcription
- [ ] Handle errors (no audio, bad format, etc.)

**Tests:**
```bash
# Test with audio file
curl -X POST http://localhost:8000/api/voice/transcribe \
  -F "audio=@path/to/audio.wav" \
  -F "user_id=test"
```

**Checklist:**
- [ ] Accepts WAV/MP3 audio
- [ ] Returns transcribed text
- [ ] Error handling for bad files
- [ ] Performance acceptable (<5s for normal audio)

### Deliverables (Mid Week 3)
- ✅ Whisper STT working
- ✅ Transcription endpoint
- ✅ Audio file handling

---

## PHASE 1D: Voice I/O - TTS (Week 3b)
**Timeline:** Sept 27-28  
**Goal:** Text-to-speech output

### Day 1: pyttsx3 Setup (Sept 27)
- [ ] Install pyttsx3
- [ ] Create TTS endpoint
- [ ] Test basic speech output

```bash
pip install pyttsx3
```

**Checklist:**
- [ ] pyttsx3 installed
- [ ] Basic speak() working
- [ ] Audio output working

### Day 2: Voice Output Endpoint (Sept 28)
- [ ] Create `/api/voice/speak` endpoint
- [ ] Accept text input
- [ ] Return audio file
- [ ] Handle speed/voice options

**Tests:**
```bash
# Test TTS
curl -X POST http://localhost:8000/api/voice/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice_speed": 1.0}' \
  > output.wav
```

**Checklist:**
- [ ] Generates audio from text
- [ ] Returns audio file
- [ ] Speed adjustment working
- [ ] Error handling for empty text

### Deliverables (End of Week 3)
- ✅ Speech-to-text working
- ✅ Text-to-speech working
- ✅ Voice endpoints integrated
- ✅ End-to-end voice chat possible

---

## PHASE 1E: Tools & Features (Week 4)
**Timeline:** Oct 1-5  
**Goal:** Basic tools (weather, web search)

### Simple Tools to Implement

#### Tool 1: Weather (Oct 1-2)
- [ ] Create `/api/tools/weather` endpoint
- [ ] Accept location parameter
- [ ] Call weather API (free: openweathermap.org)
- [ ] Return formatted weather data
- [ ] Integrate into LLM context

```python
# Free API: https://openweathermap.org/api
# Endpoint: api.openweathermap.org/data/2.5/weather?q={city}&units=metric
```

**Checklist:**
- [ ] Weather endpoint working
- [ ] Real-time data from API
- [ ] Error handling for bad locations
- [ ] LLM aware of weather tool

#### Tool 2: Web Search (Oct 3-4)
- [ ] Create `/api/tools/search` endpoint
- [ ] Accept search query
- [ ] Use free API (duckduckgo or google custom search)
- [ ] Return search results
- [ ] Integrate into LLM context

```python
# Free: DuckDuckGo search (no API key)
# Or: Google Custom Search (free tier = 100 queries/day)
```

**Checklist:**
- [ ] Search endpoint working
- [ ] Results relevant
- [ ] Error handling for bad queries
- [ ] Integrates with chat

#### Tool 3: Time/Date (Oct 5)
- [ ] Create `/api/tools/time` endpoint
- [ ] Return current time with timezone
- [ ] Test timezone handling

**Checklist:**
- [ ] Returns current time
- [ ] Timezone support

### Deliverables (End of Week 4)
- ✅ Weather tool working
- ✅ Web search tool working
- ✅ Time tool working
- ✅ Tools integrated with chat

---

## PHASE 1F: Testing & Polish (Week 5)
**Timeline:** Oct 8-12  
**Goal:** Quality assurance and documentation

### Unit Tests
- [ ] Test models validation
- [ ] Test database operations
- [ ] Test LLM service
- [ ] Test voice service
- [ ] Test tool integrations

```bash
# Run tests
pytest tests/ -v

# Coverage report
pytest --cov=backend tests/
```

### Integration Tests
- [ ] Test full chat flow
- [ ] Test voice I/O flow
- [ ] Test tool integration
- [ ] Test multi-user scenarios
- [ ] Test error scenarios

### Documentation
- [ ] Complete README.md
- [ ] Write API_DOCUMENTATION.md
- [ ] Create ARCHITECTURE.md with diagrams
- [ ] Write SETUP_GUIDE.md
- [ ] Create TROUBLESHOOTING.md
- [ ] Add code comments

### Performance Testing
- [ ] Test response time (<2s for chat)
- [ ] Test concurrent users (5+ simultaneous)
- [ ] Test database query performance
- [ ] Test memory usage
- [ ] Load testing

### Deliverables (End of Week 5)
- ✅ 80%+ test coverage
- ✅ Complete documentation
- ✅ Performance verified
- ✅ Bug-free (known issues documented)

---

## PHASE 1G: Preparation & Launch (Week 6)
**Timeline:** Oct 15-20  
**Goal:** Ready for GitHub and portfolio

### Code Quality
- [ ] Run black formatter: `black backend/`
- [ ] Run flake8 linter: `flake8 backend/`
- [ ] Run mypy type checker: `mypy backend/`
- [ ] Final code review
- [ ] Remove debug code

### GitHub Preparation
- [ ] Create .gitignore
- [ ] Setup README with badges
- [ ] Create CONTRIBUTING.md
- [ ] Setup GitHub Actions (CI/CD)
- [ ] Create LICENSE file

### Portfolio Assets
- [ ] Screenshot of API docs
- [ ] Screenshot of chat output
- [ ] Demo video (2-3 min) showing:
  - [ ] Voice input
  - [ ] Chat with context
  - [ ] Tool integration (weather)
  - [ ] Multi-turn conversation
- [ ] Write project summary

### Final Testing
- [ ] End-to-end test (voice → LLM → voice)
- [ ] Test on clean machine (fresh install)
- [ ] Verify all docs are accurate
- [ ] Check for typos/errors
- [ ] Performance benchmarks

### Deliverables (End of Week 6)
- ✅ Clean, production-ready code
- ✅ Complete documentation
- ✅ Ready for GitHub release
- ✅ Portfolio-quality demo
- ✅ LinkedIn post ready

---

## SUCCESS CRITERIA

By end of Phase 1, you should have:

### Functional
- ✅ Chat works via text or voice
- ✅ Remembers conversations
- ✅ Understands context
- ✅ Accesses weather/search tools
- ✅ Works offline (Ollama local)

### Code Quality
- ✅ Well-organized structure
- ✅ Comprehensive error handling
- ✅ Proper logging
- ✅ Full test coverage
- ✅ Follows best practices (PEP 8)

### Documentation
- ✅ README with setup instructions
- ✅ API documentation complete
- ✅ Architecture documented
- ✅ Deployment guide
- ✅ Troubleshooting guide

### Portfolio
- ✅ GitHub repo clean & organized
- ✅ Impressive README with badges
- ✅ Demo video showing features
- ✅ Ready for LinkedIn post
- ✅ Hiring signal: "Production quality"

---

## WEEKLY STAND-UP CHECKLIST

### Week 1 Check-in
- [ ] Foundation implemented
- [ ] Ollama integrated
- [ ] Database working
- [ ] API docs generated

### Week 2 Check-in
- [ ] Conversation history working
- [ ] Memory layer functional
- [ ] User preferences saved

### Week 3 Check-in
- [ ] Speech-to-text working
- [ ] Text-to-speech working
- [ ] Voice endpoint integrated

### Week 4 Check-in
- [ ] Weather tool working
- [ ] Web search working
- [ ] Tools integrated with chat

### Week 5 Check-in
- [ ] 80%+ test coverage
- [ ] Documentation complete
- [ ] Performance verified

### Week 6 Check-in
- [ ] Code formatted & linted
- [ ] GitHub ready
- [ ] Portfolio assets ready
- [ ] Ready to ship!

---

## NEXT STEPS AFTER PHASE 1

### Phase 2 (Week 7-8): Advanced Features
- Computer vision (image recognition)
- Email integration
- Calendar integration
- Personal knowledge base
- Advanced memory/embeddings

### Phase 3 (Week 9-10): UI/Frontend
- Web interface
- Desktop app (Electron)
- Mobile app
- Dashboard

### Phase 4 (Week 11-12): Polish & Launch
- Performance optimization
- Security hardening
- Deployment to cloud
- LinkedIn launch campaign
- GitHub showcase

---

## RESOURCES

### Learning
- FastAPI docs: https://fastapi.tiangolo.com/
- Pydantic docs: https://docs.pydantic.dev/
- SQLite docs: https://www.sqlite.org/docs.html
- Ollama docs: https://github.com/ollama/ollama
- Whisper docs: https://github.com/openai/whisper

### Tools
- API Testing: https://www.postman.com/ (free)
- Database Browser: https://sqlitebrowser.org/
- Code Formatter: `pip install black`
- Linter: `pip install flake8`

### APIs (Free Tier)
- Weather: https://openweathermap.org/api
- Search: https://duckduckgo.com/
- Time/Date: Built-in Python

---

## ESTIMATED TIME BREAKDOWN

| Phase | Week | Hours | Focus |
|-------|------|-------|-------|
| 1A | 1 | 15 | Foundation & Ollama |
| 1B | 2 | 12 | Database & Memory |
| 1C | 3a | 6 | Speech-to-Text |
| 1D | 3b | 6 | Text-to-Speech |
| 1E | 4 | 15 | Tools & Integration |
| 1F | 5 | 18 | Testing & Quality |
| 1G | 6 | 12 | Polish & Launch |
| **TOTAL** | **6 weeks** | **~84 hours** | **MVP Complete** |

**Per week:** ~14 hours (2 hours/day, 5 days/week)  
**Feasible?** YES ✅ (You have 11+ weeks, only need 6)

---

## LET'S SHIP THIS! 🚀

This is a **solid, achievable** roadmap. By following it week-by-week, you'll have:

1. A **production-quality** AI assistant
2. **Impressive portfolio** project
3. **Real engineering** credentials
4. **GitHub** presence
5. **Strong hiring signal** for AI jobs

**Start with Phase 1A today. Questions? Ask as you go!**
