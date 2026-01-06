# DevSwarm 🚀

**8 AI Agents Building Software Autonomously**

DevSwarm is a local-first desktop application where eight specialized AI agents collaborate as a software development team, building applications from natural language descriptions.

## 🤖 Meet the Team

1. **Sarah Chen** - Product Manager
2. **Marcus Williams** - Software Architect
3. **Elena Rodriguez** - Frontend Developer
4. **James Okonkwo** - Backend Developer
5. **Priya Sharma** - DevOps Engineer
6. **David Kim** - Security Engineer
7. **Aisha Patel** - QA Engineer
8. **Oliver Hansen** - Project Coordinator

## 🏗️ Architecture

- **Frontend**: Electron + Next.js 14 + React + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI + llama-cpp-python
- **Model**: Phi-4-multimodal (Q4_K_M quantization, ~4GB VRAM)
- **Protocol**: MCP (Model Context Protocol) for tool integration
- **Storage**: SQLite + JSON event store

## 📋 Requirements

- **GPU**: 6GB VRAM minimum (NVIDIA)
- **RAM**: 16GB minimum
- **Storage**: 10GB for model + application
- **OS**: Windows 10/11, macOS, or Linux

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd devswarm
```

### 2. Install Dependencies

```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 3. Download Model

Download Phi-4-multimodal Q4_K_M GGUF model and place in `models/` directory:

```bash
# Create models directory
mkdir models

# Download model (example using huggingface-cli)
huggingface-cli download microsoft/phi-4-multimodal --include "*.gguf" --local-dir models/
```

### 4. Run Development Mode

```bash
# Start both frontend and backend
npm run dev

# Or start separately:
npm run dev:frontend  # Frontend on http://localhost:3001
npm run dev:backend   # Backend on http://localhost:8000
```

### 5. Run Electron App

```bash
# Build frontend first
cd frontend && npm run build && cd ..

# Start Electron app
npm run electron:dev
```

## 📁 Project Structure

```
devswarm/
├── frontend/              # Electron + Next.js frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── lib/          # Utilities
│   │   └── types/        # TypeScript types
│   ├── electron/         # Electron main process
│   └── public/           # Static assets
├── backend/              # Python FastAPI backend
│   ├── api/             # REST endpoints
│   ├── agents/          # Agent definitions
│   ├── tools/           # MCP tools
│   ├── models/          # Model management
│   ├── memory/          # Session management
│   ├── events/          # Event store
│   └── orchestration/   # Agent coordination
└── models/              # GGUF model files
```

## 🛠️ Development Roadmap

- [x] **Phase 1**: Foundation Infrastructure (Weeks 1-2)
- [ ] **Phase 2**: Core Agent Implementation (Weeks 3-4)
- [ ] **Phase 3**: Tool Integration (Weeks 5-6)
- [ ] **Phase 4**: Visualization (Weeks 7-8)
- [ ] **Phase 5**: Advanced Capabilities (Weeks 9-10)
- [ ] **Phase 6**: Polish & Release (Weeks 11-12)

## 🎯 Key Features

### Shared Brain Architecture
Single Phi-4-multimodal instance serving all 8 agents with isolated memory contexts

### Real-Time Visualization
Watch agents collaborate in real-time with terminal output and git-like commit history

### Tool Ecosystem
30+ tools including filesystem operations, GitHub integration, testing, security scanning

### Event Sourcing
Complete audit trail of all agent actions and decisions

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [Brain System](docs/brain.md)
- [Tool Ecosystem](docs/tools.md)
- [Frontend Design](docs/design.md)

## 🤝 Contributing

This is an early-stage project. Contributions welcome!

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [Phi-4-multimodal](https://huggingface.co/microsoft/phi-4-multimodal)
- Uses [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Inspired by multi-agent AI systems

---

**Status**: Phase 1 - Foundation Infrastructure ✅
