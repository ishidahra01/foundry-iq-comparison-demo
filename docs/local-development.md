# Local Development Guide

This project now assumes real Azure-backed execution for both comparison and evaluation flows.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Azure CLI
- Access to an Azure AI Foundry Project with both agents configured
- An evaluator deployment for LLM-based scoring

## Setup

1. Clone the repository.

```bash
git clone https://github.com/ishidahra01/foundry-iq-comparison-demo.git
cd foundry-iq-comparison-demo
```

1. Create `.env` from `.env.example` and fill in your project values.

```bash
cp .env.example .env
```

Minimum configuration:

```dotenv
AZURE_AI_PROJECT_ENDPOINT=https://your-ai-services-account.services.ai.azure.com/api/projects/your-project-name
CLASSIC_RAG_AGENT_NAME=classic-rag-agent
FOUNDRY_IQ_AGENT_NAME=foundry-iq-agent
EVALUATION_MODEL=your-evaluator-deployment-name
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Notes:

- `EVALUATION_MODEL` is required only for the JSONL-based evaluation flow.
- Comparison works without `EVALUATION_MODEL`, but `/compare/evaluate` will return `not_configured`.

1. Authenticate locally.

```bash
az login
```

1. Start the backend.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verify:

```bash
curl http://localhost:8000/health
```

1. Start the frontend in a second terminal.

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Main Local Workflows

### Standard Comparison

1. Enter a question.
1. Run the compare flow.
1. Inspect both answer panels, tool execution, trace events, and difference cards.

### Ground-Truth Evaluation

1. Use the bundled sample selector or paste one JSONL row.
1. Let the UI populate the question field.
1. Run evaluation.
1. Review the ground truth, evidence, evaluator summary, winner, and per-agent scores.

The default bundled showcase case is `zava_agentic_004` from `sample-data/zava-sample/agentic_retrieval_eval_10.jsonl`.

## Useful API Checks

### Health

```bash
curl http://localhost:8000/health
```

### Compare

```bash
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"question": "匿名で不正を通報したい一方で、自分の個人情報の訂正も依頼したい contractor から相談された。窓口をどう切り分けるべきか。"}'
```

### List Evaluation Cases

```bash
curl http://localhost:8000/evaluation/cases
```

### Compare And Evaluate

```bash
curl -X POST http://localhost:8000/compare/evaluate \
  -H "Content-Type: application/json" \
  -d '{"evaluation_sample_id": "zava_agentic_004"}'
```

## Development Notes

### Backend Files

```text
backend/
├── main.py
├── agent_client.py
├── evaluator.py
├── models.py
└── requirements.txt
```

### Frontend Files

```text
frontend/
├── app/
├── components/
└── package.json
```

### Validation

- Frontend: `npm run build`
- Backend syntax: `python -m compileall backend`

## Troubleshooting

### `AZURE_AI_PROJECT_ENDPOINT is required`

Your `.env` is missing the Azure AI Project endpoint.

### Authentication errors

Run `az login` again, then retry the backend request.

### Evaluation returns `not_configured`

Set `EVALUATION_MODEL` to a valid Foundry deployment name.

### One agent fails but the UI still renders

This is expected behavior. The API returns partial results together with the captured agent error.
