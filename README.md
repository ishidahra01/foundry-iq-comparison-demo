# Foundry IQ Comparison Demo

This application compares **Classic RAG** and **Foundry IQ Agentic Retrieval** side-by-side on the same question, then optionally evaluates both answers against a JSONL ground-truth dataset.

## What It Demonstrates

- Side-by-side answer comparison for Classic RAG and Foundry IQ
- Deterministic comparison metrics such as query count, tool calls, source reach, and retrieved evidence volume
- Rich answer inspection including Markdown rendering, citations, sources, query plans, and trace events
- Ground-truth evaluation using a Foundry-hosted model through **Entra authentication**, not API keys
- Evaluation dataset workflow driven by JSONL samples or pasted JSONL rows

## Current Demo Flow

The UI now supports two main paths:

1. Standard comparison
   Enter a question and compare both retrieval approaches directly.

2. Ground-truth evaluation
   Select a bundled JSONL sample or paste a JSONL row, auto-populate the question field, run both agents, then score both answers against the supplied ground truth.

## Sample Scenario And Data

The repository currently includes two data tracks.

### 1. Comparison / Retrieval Data

The `sample-data/` directory contains the primary demo corpus used by the agents and includes policy, benefits, architecture, rollout, and budget-style content.

### 2. Evaluation Dataset

The `sample-data/zava-sample/agentic_retrieval_eval_10.jsonl` file contains evaluation cases with:

- `id`
- `question`
- `ideal_answer`
- `evidence[]`

The default evaluation sample used in the UI is:

- `zava_agentic_004`
- Question: `匿名で不正を通報したい一方で、自分の個人情報の訂正も依頼したい contractor から相談された。窓口をどう切り分けるべきか。`

This case is useful because it requires policy routing across multiple intents:

- anonymous whistleblower reporting
- privacy / personal information correction
- contractor eligibility

## Architecture

### Backend

- FastAPI API service
- Azure AI Projects 2.x integration via `AIProjectClient` and the Responses API
- Entra-authenticated agent invocation for both comparison agents
- Entra-authenticated evaluator model invocation for ground-truth scoring

### Frontend

- Next.js App Router
- Tailwind CSS
- Comparison UI, timeline view, evaluation input flow, and evaluation result rendering

## Requirements

- Python 3.11+
- Node.js 18+
- An Azure AI Foundry Project endpoint
- Two configured agents:
  - `classic-rag-agent`
  - `foundry-iq-agent`
- A Foundry-hosted evaluator model deployment name for LLM-based scoring
- Entra auth available locally, typically through `az login`

## Setup

1. Clone the repository.

```bash
git clone https://github.com/ishidahra01/foundry-iq-comparison-demo.git
cd foundry-iq-comparison-demo
```

1. Create and configure `.env` from `.env.example`.

Required values:

```dotenv
AZURE_AI_PROJECT_ENDPOINT=https://your-ai-services-account.services.ai.azure.com/api/projects/your-project-name
CLASSIC_RAG_AGENT_NAME=classic-rag-agent
FOUNDRY_IQ_AGENT_NAME=foundry-iq-agent
EVALUATION_MODEL=your-evaluator-deployment-name
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

1. Sign in for Entra-based local development.

```bash
az login
```

1. Start the backend.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

1. Start the frontend.

```bash
cd frontend
npm install
npm run dev
```

1. Open `http://localhost:3000`.

## Key UI Features

### Comparison View

- Side-by-side Classic RAG and Foundry IQ result panels
- Answer rendering in Markdown
- Citations and sources shown only when available
- Query-plan and execution visibility
- Deterministic difference cards showing:
  - query expansion
  - tool routing
  - source reach
  - evidence volume

### Ground Truth Evaluation View

- Bundled sample selection from JSONL metadata
- Pasted JSONL row execution
- Auto-population of the question field from evaluation input
- Ground truth display with ideal answer and evidence
- Evaluator summary, winner, and per-agent scoring

The evaluator is instructed to write all natural-language output in the same language used by the ground-truth question and ideal answer.

## API Overview

### Core Endpoints

- `GET /health`
- `POST /compare`
- `GET /evaluation/cases`
- `POST /compare/evaluate`
- `WebSocket /ws/compare/{session_id}`

### Evaluation Example

Using a bundled sample:

```json
{
  "evaluation_sample_id": "zava_agentic_004"
}
```

Using pasted JSONL:

```json
{
  "evaluation_jsonl": "{\"id\":\"custom_001\",\"question\":\"...\",\"ideal_answer\":\"...\",\"evidence\":[...] }"
}
```

See [backend/README.md](backend/README.md) for backend-specific API and configuration details.

## Project Structure

```text
foundry-iq-comparison-demo/
├── backend/
│   ├── agent_client.py
│   ├── evaluator.py
│   ├── main.py
│   ├── models.py
│   ├── README.md
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── components/
│   ├── package.json
│   └── README.md
├── sample-data/
│   ├── zava-sample/
│   │   └── agentic_retrieval_eval_10.jsonl
│   └── ...
├── docs/
│   ├── azure-ai-search-setup.md
│   ├── foundry-iq-setup.md
│   ├── foundry-agent-setup.md
│   ├── local-development.md
│   └── azure-app-service-deployment.md
├── .env.example
└── README.md
```

## Local Development Notes

- The app no longer includes mock execution. Azure configuration is required.
- If `EVALUATION_MODEL` is unset, comparison still works, but evaluation returns `not_configured`.
- If `AZURE_AI_PROJECT_ENDPOINT` is unset, comparison and evaluation requests will fail at runtime.

## Documentation

- [Backend API Guide](backend/README.md)
- [Local Development](docs/local-development.md)
- [Azure App Service Deployment](docs/azure-app-service-deployment.md)
- [Sample Data Explanation](sample-data/README.md)

## License

MIT License. See [LICENSE](LICENSE).
