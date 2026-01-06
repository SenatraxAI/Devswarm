# DevSwarm Testing Guide

## Quick Start Testing

### Prerequisites
- Node.js 18+ installed
- Python 3.10+ installed
- Git bash or PowerShell

---

## Step 1: Install Dependencies

### Frontend Dependencies
```bash
cd devswarm/frontend
npm install
```

### Backend Dependencies
```bash
# From devswarm root
cd backend
pip install -r requirements.txt
```

---

## Step 2: Start Backend Server

```bash
# From devswarm/backend directory
python main.py
```

**Expected Output:**
```
🚀 Starting DevSwarm Backend...
📦 Loading Phi-4-multimodal model...
✅ DevSwarm Backend ready!
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test Backend Health:**
Open browser to: http://localhost:8000/health

Should see:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "agents_ready": true,
  "vram_usage_gb": 4.2
}
```

---

## Step 3: Start Frontend (Development Mode)

```bash
# In a NEW terminal, from devswarm/frontend directory
npm run dev
```

**Expected Output:**
```
▲ Next.js 14.1.0
- Local:        http://localhost:3001
- Network:      http://192.168.x.x:3001

✓ Ready in 2.3s
```

Open browser to: **http://localhost:3001**

---

## Step 4: Verify WebSocket Connection

In the browser (http://localhost:3001), open Developer Console (F12):

**Look for:**
```
✅ WebSocket connected
```

**You should see:**
- Header shows "Connected" with green indicator
- "8 agents ready" in header
- Agent Team panel on left (currently empty)
- Live Chat in center
- Terminal panel on right

---

## Step 5: Test Real-Time Updates (Optional)

Run the WebSocket test script to simulate agent activity:

```bash
# In a NEW terminal, from devswarm root
python test_websocket.py
```

**Expected Output:**
```
🧪 Starting agent activity simulation...
📢 Sarah Chen: Thinking...
📢 Sarah Chen: Speaking...
📢 Marcus Williams: Thinking...
📢 Marcus Williams: Speaking...
💻 Terminal: Output...
📝 Code change...
✅ Simulation complete
```

**In the browser, you should see:**
- Agent status indicators changing (idle → thinking → speaking)
- Messages appearing in the Live Chat panel
- Terminal output appearing in the Terminal panel
- Agent cards glowing when active

---

## Troubleshooting

### Backend won't start
**Error:** `ModuleNotFoundError: No module named 'fastapi'`
**Fix:** Make sure you're in the `backend` directory and run:
```bash
pip install -r requirements.txt
```

### Frontend won't start
**Error:** `Cannot find module 'next'`
**Fix:** Make sure you're in the `frontend` directory and run:
```bash
npm install
```

### WebSocket not connecting
**Check:**
1. Backend is running on port 8000
2. Frontend is running on port 3001
3. No firewall blocking localhost connections
4. Browser console for error messages

### Port already in use
**Backend (port 8000):**
```bash
# Windows - kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Frontend (port 3001):**
```bash
# Change port in package.json
"dev": "next dev -p 3002"
```

---

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] Frontend loads at localhost:3001
- [ ] WebSocket connects (green indicator in header)
- [ ] Agent team panel shows 8 agents
- [ ] test_websocket.py shows agent activity in browser
- [ ] Terminal output appears in right panel
- [ ] Messages appear in center panel

---

## Current Limitations

⚠️ **Note:** This is Phase 1.2 - Basic infrastructure only!

**What works:**
- ✅ WebSocket connection
- ✅ Real-time message broadcasting
- ✅ UI updates from backend events

**What's simulated (not yet implemented):**
- ⏳ Actual model loading (Phi-4-multimodal)
- ⏳ Real agent inference
- ⏳ MCP tool integration
- ⏳ File system operations
- ⏳ Code generation

**Coming in Phase 1.3-1.4:**
- MCP Server integration (Filesystem, GitHub, Context7)
- Real agent sessions
- Actual model inference

---

## Next Steps

Once testing is complete and WebSocket connection works:
1. **Phase 1.3**: Integrate MCP servers (Filesystem, Context7, GitHub)
2. **Phase 1.4**: Implement basic agent framework with Phi-4 model
3. **Phase 2**: Add agent personalities and communication patterns

Happy testing! 🚀
