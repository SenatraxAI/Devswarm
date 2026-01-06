# DevSwarm Debugging Guide

## Quick Diagnosis

Run these commands in order to find the issue:

### 1. Check Ollama Status
```bash
curl http://localhost:11434/api/tags
```
**Expected:** JSON response with model list
**If fails:** Ollama not running → Run `ollama serve` in another terminal

### 2. Check Available Models
```bash
ollama list
```
**Expected:** See `gemma3:4b` or `gemma3:1b` in the list
**If missing:** Run `ollama pull gemma3:4b`

### 3. Test Model Directly
```bash
ollama run gemma3:4b "Hi, introduce yourself"
```
**Expected:** Model responds with introduction
**If fails:** Model not working → Try `ollama pull gemma3:4b` again

### 4. Test Backend Model Integration
```bash
cd backend
python test_gemma.py
```
**Expected:** See Sarah Chen introduce herself
**If fails:** Check error message

### 5. Start Backend with Logs
```bash
cd backend
python main.py
```
**Look for:**
```
📦 Initializing ModelManager...
🔗 Connecting to Ollama at http://localhost:11434
✅ Model 'gemma3:4b' ready
```

**If you see:**
- `⚠️ Model 'gemma3:4b' not found` → Model name mismatch
- `❌ Failed to connect to Ollama` → Ollama not running
- `❌ Ollama API error` → Ollama issue

### 6. Check Frontend Connection
1. Open browser console (F12)
2. Go to http://localhost:3001
3. Look for WebSocket connection messages

**Expected:**
```
WebSocket connected
Received: {type: "connection", status: "connected"}
```

---

## Common Issues & Fixes

### Issue 1: "No response showing"
**Cause:** Backend not running or crashed
**Fix:** 
1. Check backend terminal for errors
2. Restart: `cd backend && python main.py`

### Issue 2: "Model 'gemma3:4b' not found"
**Cause:** Model name doesn't match
**Fix:**
1. Run `ollama list` to see actual model names
2. If you see `gemma3:1b`, update `backend/models/model_manager.py` line 25:
   ```python
   self.model_name = "gemma3:1b"  # Change from gemma3:4b
   ```

### Issue 3: "Ollama connection failed"
**Cause:** Ollama not running
**Fix:**
1. Open new terminal
2. Run `ollama serve`
3. Restart backend

### Issue 4: "WebSocket disconnected"
**Cause:** Backend crashed or not running
**Fix:**
1. Check backend terminal for errors
2. Look for Python traceback
3. Share error with me

---

## Step-by-Step Startup

**Terminal 1 (Ollama):**
```bash
ollama serve
```
Keep this running!

**Terminal 2 (Backend):**
```bash
cd backend
python main.py
```
Wait for `✅ Model 'gemma3:4b' ready`

**Terminal 3 (Frontend):**
```bash
cd frontend
npm run dev
```

**Browser:**
- Go to http://localhost:3001
- Type: `@Sarah Chen hi`
- Press Send

---

## What to Check Right Now

1. **Is Ollama running?**
   - Check Task Manager for "ollama" process
   - OR run `curl http://localhost:11434/api/tags`

2. **Is backend running?**
   - Check terminal for errors
   - Look for "Uvicorn running on http://0.0.0.0:8765"

3. **Is frontend connected?**
   - Open browser console (F12)
   - Look for WebSocket messages

**Share with me:**
- What do you see in the backend terminal?
- Any errors in browser console (F12)?
- Output of `ollama list`
