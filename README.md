# Foundry IQ Comparison Demo

A comprehensive demo application that compares **Classic RAG** (Azure AI Search) and **Foundry IQ** (Agentic Retrieval) side-by-side, showcasing the differences in:

- Answer quality and comprehensiveness
- Retrieval strategies and query decomposition
- Processing steps and tool usage
- Citations and source attribution
- Performance metrics

## 🎯 Purpose

This demo demonstrates the value proposition of **Foundry IQ's Agentic Retrieval** compared to traditional RAG approaches by:

1. **Visual Comparison**: Side-by-side agent results with rich metrics
2. **Process Transparency**: Real-time execution traces showing how each agent works
3. **Quantitative Metrics**: Performance, token usage, retrieval counts
4. **Realistic Scenario**: Go/No-Go launch advisor with complex multi-document analysis

## 📋 Prerequisites

### Required (for full functionality)
- **Python 3.11+**
- **Node.js 18+** and npm
- **Azure subscription** with:
  - Azure AI Search (with sample data indexed)
  - Azure AI Foundry Project with 2 agents configured
  - Foundry IQ knowledge base

### Optional (for local testing)
- None! The app works in **mock mode** without Azure connectivity

## 🚀 Quick Start (Mock Mode)

**Test locally without Azure setup:**

1. Clone the repository:
```bash
git clone https://github.com/ishidahra01/foundry-iq-comparison-demo.git
cd foundry-iq-comparison-demo
```

2. Start the backend (mock mode):
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend will run on **http://localhost:8000** in mock mode (no Azure required).

3. Start the frontend (in a new terminal):
```bash
cd frontend
npm install
npm run dev
```

Frontend will run on **http://localhost:3000**.

4. Open http://localhost:3000 and try a sample query!

## 🔧 Full Setup (with Azure)

### Step 1: Azure Resources Setup

#### 1.1 Create Azure AI Search Index

1. Create an Azure AI Search service (Standard tier or higher)
2. Create a new index with these settings:
   - Enable vector search
   - Enable semantic search (if available)
   - Text + vector fields

3. Index the sample data:
```bash
# Install Azure CLI and login
az login

# Index documents from sample-data/ directory
# Use Azure AI Search indexer or upload via SDK/API
```

See `/docs/azure-ai-search-setup.md` for detailed instructions.

#### 1.2 Create Foundry IQ Knowledge Base

1. Go to Azure AI Foundry portal
2. Create a new Knowledge Base
3. Add the sample data documents from `sample-data/`
4. Configure for **Agentic Retrieval** mode
5. Note the knowledge base ID

See `/docs/foundry-iq-setup.md` for detailed instructions.

#### 1.3 Create Foundry Agents

Create **two agents** in your Azure AI Foundry Project:

**Agent 1: classic-rag-agent**
- Name: `classic-rag-agent`
- Description: "Classic RAG using Azure AI Search"
- Tools: Azure AI Search connector
- Configuration: Single-step retrieval

**Agent 2: foundry-iq-agent**
- Name: `foundry-iq-agent`
- Description: "Agentic Retrieval using Foundry IQ"
- Tools: Foundry IQ knowledge base
- Configuration: Enable query decomposition, multi-step retrieval

See `/docs/foundry-agent-setup.md` for detailed instructions.

### Step 2: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your Azure credentials:
```bash
# Azure AI Projects 2.x
AZURE_AI_PROJECT_ENDPOINT=https://your-ai-services-account.services.ai.azure.com/api/projects/your-project-name

# Agent Names
CLASSIC_RAG_AGENT_NAME=classic-rag-agent
FOUNDRY_IQ_AGENT_NAME=foundry-iq-agent

# Disable mock mode
MOCK_MODE=false
```

### Step 3: Run the Application

1. Start backend:
```bash
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python main.py
```

2. Start frontend:
```bash
cd frontend
npm run dev
```

3. Access at http://localhost:3000

## 📂 Project Structure

```
foundry-iq-comparison-demo/
├── backend/                    # FastAPI backend
│   ├── main.py                # API endpoints and WebSocket
│   ├── models.py              # Pydantic data models
│   ├── agent_client.py        # Azure AI Projects Responses API client
│   ├── mock_responses.py      # Mock data generator
│   └── requirements.txt       # Python dependencies
├── frontend/                   # Next.js frontend
│   ├── app/                   # Next.js app directory
│   │   ├── page.tsx           # Main page
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── QueryInput.tsx     # Question input
│   │   ├── ComparisonView.tsx # Main comparison UI
│   │   ├── AgentResultPanel.tsx # Agent result display
│   │   └── ProcessingWindow.tsx # Execution timeline
│   └── package.json           # Node dependencies
├── sample-data/               # Demo data for indexing
│   ├── 01_project_overview.md
│   ├── 02_architecture_decision.md
│   ├── 03_security_policy.md
│   ├── 04_preview_feature_policy.md
│   ├── 05_budget_guardrail.md
│   ├── 06_rollout_plan.md
│   ├── 07_open_issues.md
│   ├── 08_exception_process.md
│   └── README.md              # Data explanation
├── docs/                      # Documentation
│   ├── azure-ai-search-setup.md
│   ├── foundry-iq-setup.md
│   ├── foundry-agent-setup.md
│   ├── local-development.md
│   └── azure-app-service-deployment.md
├── .env.example               # Environment template
├── .gitignore
├── LICENSE
└── README.md                  # This file
```

## 🎨 Key Features

### 1. Side-by-Side Comparison
- Compare answers from both agents in parallel
- Visual verdict display (Go / Conditional / No-Go)
- Performance metrics (time, tokens, sources, citations)

### 2. Processing Timeline
- Real-time execution trace
- Event-by-event visualization
- Agent differentiation with color coding
- Relative timestamps showing execution order

### 3. Rich Agent Details
- **Answer**: Full response with formatting
- **Citations**: Source documents with relevance scores
- **Execution Details**: Performance metrics, sources, query plans
- **Trace Events**: Step-by-step execution log

### 4. Sample Queries
- Pre-configured queries of varying complexity
- Simple → Medium → Complex demonstration
- Japanese language support

## 🧪 Testing the Demo

### Simple Query (Both agents perform similarly)
```
What is the project timeline?
```

### Medium Complexity (Foundry IQ shows advantage)
```
Are there any security blockers for the launch?
```

### High Complexity (Foundry IQ significant advantage)
```
Should we launch this AI feature on April 30? What are the main risks and blockers?
```

### Expected Differences

**Classic RAG:**
- Single keyword-based retrieval
- Surface-level answer
- Fewer citations
- Faster execution (simpler process)

**Foundry IQ:**
- Query decomposition into sub-queries
- Multi-step retrieval
- Comprehensive analysis with synthesis
- More citations from diverse sources
- Longer execution (more thorough process)

## 📊 Demo Scenario

**Go/No-Go Launch Advisor**

The sample data represents a realistic enterprise scenario:
- AI feature planning to launch April 30, 2026
- Multiple policy documents (security, budget, preview features)
- Open issues and blockers
- Timeline dependencies
- Budget constraints

**Key Question:**
> "Should we launch this AI feature on April 30? Considering internal policies, current implementation status, and budget constraints, provide Go/No-Go recommendation, blockers, and next actions."

**Expected Results:**
- **Classic RAG**: Identifies some issues, surface-level analysis
- **Foundry IQ**: Comprehensive analysis, identifies critical blockers (security assessment conflict, PII redaction), provides conditional recommendation with specific next actions

## 🚢 Deployment

### Local Development
See `/docs/local-development.md`

### Azure App Service
See `/docs/azure-app-service-deployment.md`

Quick deployment:
```bash
# Backend deployment
az webapp up --runtime PYTHON:3.11 --name your-backend-name

# Frontend deployment
npm run build
az webapp up --runtime NODE:18-lts --name your-frontend-name
```

## 📚 Documentation

- [Azure AI Search Setup](docs/azure-ai-search-setup.md)
- [Foundry IQ Setup](docs/foundry-iq-setup.md)
- [Foundry Agent Setup](docs/foundry-agent-setup.md)
- [Local Development](docs/local-development.md)
- [Azure App Service Deployment](docs/azure-app-service-deployment.md)
- [Sample Data Explanation](sample-data/README.md)

## 🔍 API Reference

### Backend Endpoints

#### `GET /health`
Health check

#### `POST /compare`
Synchronous comparison
```json
{
  "question": "Your question here"
}
```

#### `WebSocket /ws/compare/{session_id}`
Real-time streaming comparison

#### `GET /sample-queries`
Get sample queries for testing

#### `POST /sessions`
Create a new session

#### `GET /sessions`
List all sessions

See backend README for full API documentation.

## 🛠️ Development

### Backend Development
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
# Backend tests (if added)
cd backend
pytest

# Frontend tests (if added)
cd frontend
npm test
```

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.11+)
- Verify virtual environment is activated
- Check port 8000 is available

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Delete `node_modules` and `package-lock.json`, reinstall
- Check port 3000 is available

### Can't connect to Azure
- Verify `.env` file has correct credentials
- Check `MOCK_MODE=false` to use real agents
- Verify agent names match your Foundry Agent Service

### Mock mode not working
- Ensure `MOCK_MODE=true` (or just don't set Azure credentials)
- Backend should log "⚠️ Running in MOCK MODE"

## 🤝 Contributing

This is a demo repository. For issues or suggestions:
1. Open an issue on GitHub
2. Describe the problem or enhancement
3. Include screenshots if UI-related

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- UI inspired by [aitour-site-approval-bot](https://github.com/ishidahra01/aitour-site-approval-bot)
- Built with [Next.js](https://nextjs.org/), [FastAPI](https://fastapi.tiangolo.com/), [Tailwind CSS](https://tailwindcss.com/)
- Azure AI Foundry, Azure AI Search, Azure OpenAI Service

## 📞 Support

For questions about:
- **This demo**: Open a GitHub issue
- **Foundry IQ**: See [official documentation](https://learn.microsoft.com/azure/ai-studio/)
- **Azure AI Search**: See [official documentation](https://learn.microsoft.com/azure/search/)

---

**Built to demonstrate Foundry IQ's Agentic Retrieval capabilities** 🚀
