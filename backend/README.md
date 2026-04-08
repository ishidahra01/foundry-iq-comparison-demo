# Backend API Documentation

The backend runs the comparison workflow for Classic RAG and Foundry IQ, then optionally evaluates both answers against JSONL ground truth using a Foundry-hosted model.

This service is Azure-only. Mock execution has been removed.

## Responsibilities

- Execute both agents through Azure AI Projects 2.x
- Stream trace events to the UI over WebSocket
- Parse response payloads into normalized citations, sources, documents, query plans, and token metrics
- Load bundled evaluation cases from `sample-data/zava-sample/agentic_retrieval_eval_10.jsonl`
- Evaluate both answers against ground truth using a Foundry deployment through Entra authentication

## Run Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

For reload during development:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API is available at `http://localhost:8000`.

## Required Configuration

```dotenv
AZURE_AI_PROJECT_ENDPOINT=https://your-ai-services-account.services.ai.azure.com/api/projects/your-project-name
CLASSIC_RAG_AGENT_NAME=classic-rag-agent
FOUNDRY_IQ_AGENT_NAME=foundry-iq-agent
EVALUATION_MODEL=your-evaluator-deployment-name
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

Authenticate locally with Entra credentials before running comparison or evaluation requests.

```bash
az login
```

## Environment Variables

| Variable | Description | Required |
| -------- | ----------- | -------- |
| `AZURE_AI_PROJECT_ENDPOINT` | Azure AI Projects 2.x endpoint | Yes |
| `CLASSIC_RAG_AGENT_NAME` | Name of Classic RAG agent | Yes |
| `CLASSIC_RAG_AGENT_VERSION` | Optional Classic RAG agent version | No |
| `FOUNDRY_IQ_AGENT_NAME` | Name of Foundry IQ agent | Yes |
| `FOUNDRY_IQ_AGENT_VERSION` | Optional Foundry IQ agent version | No |
| `EVALUATION_MODEL` | Foundry deployment name used for answer evaluation | No |
| `BACKEND_HOST` | Bind host | No |
| `BACKEND_PORT` | Bind port | No |
| `AGENT_CLIENT_DEBUG` | Enable normalized debug logging | No |
| `AGENT_CLIENT_DEBUG_RAW` | Enable raw payload logging | No |
| `AGENT_AUTO_APPROVE_MCP` | Auto-approve MCP tool execution when supported | No |

If `EVALUATION_MODEL` is omitted, `/compare/evaluate` still runs both agents but returns `status: not_configured` for evaluation.

## Endpoints

### `GET /health`

Returns service status and whether `AZURE_AI_PROJECT_ENDPOINT` is configured.

### `GET /`

Returns service metadata and endpoint list.

### `POST /sessions`

Creates an in-memory session.

### `GET /sessions`

Lists all in-memory sessions.

### `GET /sessions/{session_id}`

Fetches a session and its stored runs.

### `DELETE /sessions/{session_id}`

Deletes a session.

### `POST /compare`

Runs both agents against a question.

Request example:

```json
{
  "question": "匿名で不正を通報したい一方で、自分の個人情報の訂正も依頼したい contractor から相談された。窓口をどう切り分けるべきか。"
}
```

### `GET /evaluation/cases`

Lists bundled JSONL evaluation samples with their `id`, `question`, and source metadata.

### `POST /compare/evaluate`

Runs both agents on a ground-truth case and evaluates the two answers.

Request using a bundled sample:

```json
{
  "evaluation_sample_id": "zava_agentic_004"
}
```

Request using pasted JSONL:

```json
{
  "evaluation_jsonl": "{\"id\":\"custom_001\",\"question\":\"...\",\"ideal_answer\":\"...\",\"evidence\":[...]}"
}
```

### `WebSocket /ws/compare/{session_id}`

Streams trace events while the comparison is running.

## Response Shape Highlights

Each agent result includes:

- `answer`
- `citations`
- `trace_events`
- `metrics`
- `sources_used`
- `query_plan`
- `tool_calls`
- `documents`
- `error`

The parser reconstructs these fields from Azure AI Projects response items, including `mcp_call.output` payloads where Foundry IQ evidence is embedded.

## Evaluation Model Behavior

The evaluator prompt instructs the model to:

- score correctness, completeness, and evidence alignment
- choose a winner
- keep the output concise
- write all natural-language fields in the same language used by the ground-truth question and ideal answer

Structured output is enforced with JSON schema.

## Architecture

```text
backend/
├── agent_client.py   # Agent execution + response normalization
├── evaluator.py      # JSONL loading + evaluator model integration
├── main.py           # FastAPI endpoints + websocket handling
├── models.py         # Request/response schemas
└── requirements.txt
```

## Notes

- Session storage is in-memory only.
- CORS is open for development and should be restricted in production.
- If one agent fails, the API still returns the other result plus the captured error payload.
