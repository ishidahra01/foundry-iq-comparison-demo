# Backend API README

FastAPI backend for Foundry IQ Comparison Demo.

## Overview

This backend provides REST API endpoints and WebSocket connections for comparing Classic RAG and Foundry IQ agent responses. It integrates with Azure AI Projects 2.x agents through the Responses API and supports mock mode for local testing.

## Quick Start

```bash
# Install dependencies
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run in mock mode (no Azure required)
python main.py

# Or run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at http://localhost:8000

## Features

- **Mock Mode**: Test without Azure connectivity
- **REST API**: Synchronous agent comparison
- **WebSocket**: Real-time streaming with trace events
- **CORS**: Configured for frontend integration
- **Auto Documentation**: Swagger UI and ReDoc

## API Endpoints

### `GET /`
Root endpoint with API information

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-06T07:30:00.000Z",
  "mock_mode": true
}
```

### `POST /compare`
Synchronous agent comparison

**Request:**
```json
{
  "question": "Your question here",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "run_id": "uuid",
  "question": "Your question",
  "timestamp": "2026-04-06T07:30:00.000Z",
  "classic_rag": { /* AgentResult */ },
  "foundry_iq": { /* AgentResult */ }
}
```

### `WebSocket /ws/compare/{session_id}`
Real-time streaming comparison

**Client Message:**
```json
{
  "question": "Your question here"
}
```

**Server Events:**
```json
{"type": "run.started", "run_id": "...", "question": "..."}
{"type": "agent.event", "agent_type": "classic-rag", "event": {...}}
{"type": "agent.event", "agent_type": "foundry-iq", "event": {...}}
{"type": "run.completed", "run_id": "..."}
{"type": "error", "message": "..."}
```

### `GET /sample-queries`
Get pre-configured sample queries

**Response:**
```json
{
  "queries": [
    {
      "id": "simple-1",
      "category": "Simple",
      "text": "What is the project timeline?",
      "description": "Basic factual query"
    }
  ]
}
```

### `POST /sessions`
Create a new session

**Request:**
```json
{
  "name": "My Session"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "My Session",
  "created_at": "2026-04-06T07:30:00.000Z",
  "runs": []
}
```

### `GET /sessions`
List all sessions

### `GET /sessions/{session_id}`
Get a specific session

### `DELETE /sessions/{session_id}`
Delete a session

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AZURE_AI_PROJECT_ENDPOINT` | Azure AI Project endpoint | - | No* |
| `CLASSIC_RAG_AGENT_NAME` | Name of Classic RAG agent | `classic-rag-agent` | No |
| `CLASSIC_RAG_AGENT_VERSION` | Optional fixed version for Classic RAG agent | latest | No |
| `FOUNDRY_IQ_AGENT_NAME` | Name of Foundry IQ agent | `foundry-iq-agent` | No |
| `FOUNDRY_IQ_AGENT_VERSION` | Optional fixed version for Foundry IQ agent | latest | No |
| `MOCK_MODE` | Enable mock responses | `true` if no Azure config | No |
| `AGENT_AUTO_APPROVE_MCP` | Auto-approve MCP tool invocations such as knowledge base retrieval | `true` | No |
| `AGENT_CLIENT_DEBUG` | Log response status snapshots and stream event names | `false` | No |
| `AGENT_CLIENT_DEBUG_RAW` | Log full serialized SDK payloads for debugging | `false` | No |
| `AGENT_RESPONSE_POLL_INTERVAL_SEC` | Poll interval when agent response is still running | `0.75` | No |
| `AGENT_RESPONSE_POLL_TIMEOUT_SEC` | Max wait time for in-progress agent responses | `45` | No |
| `BACKEND_HOST` | Host to bind to | `0.0.0.0` | No |
| `BACKEND_PORT` | Port to bind to | `8000` | No |

\* Required only when `MOCK_MODE=false`

## Architecture

```
main.py
  ├── FastAPI app
  ├── CORS middleware
  ├── REST endpoints
  └── WebSocket handler
      │
      ├── agent_client.py
      │     ├── FoundryAgentClient
      │     └── Azure AI Projects Responses API client
      │
      ├── mock_responses.py
      │     └── MockResponseGenerator
      │
      └── models.py
            └── Pydantic models
```

## Data Models

### AgentResult
```python
class AgentResult(BaseModel):
    agent_type: Literal["classic-rag", "foundry-iq"]
    agent_name: str
    answer: str
    verdict: Optional[Literal["Go", "Conditional", "No-Go"]]
    citations: List[Citation]
    trace_events: List[TraceEvent]
    metrics: Metrics
    sources_used: List[str]
    query_plan: Optional[Dict[str, Any]]
    error: Optional[str]
```

### TraceEvent
```python
class TraceEvent(BaseModel):
    timestamp: str
    event_type: Literal[
        "task_hypothesis_generated",
        "tool_call_started",
        "tool_call_completed",
        "retrieval_started",
        "retrieval_completed",
        "answer_synthesis_started",
        "answer_completed",
        "error"
    ]
    status: Literal["pending", "running", "completed", "failed"]
    elapsed_ms: Optional[int]
    mode: Literal["classic-rag", "foundry-iq"]
    metadata: Dict[str, Any]
```

## Mock Mode

Mock mode generates realistic agent responses without Azure connectivity.

**Enable:**
```bash
# Just don't set Azure credentials
python main.py

# Or explicitly
MOCK_MODE=true python main.py
```

**Characteristics:**
- Classic RAG: Faster, simpler, fewer citations
- Foundry IQ: Slower, more comprehensive, more citations
- Realistic trace events and metrics

**Mock Response Quality:**
- Pre-configured answers for demo scenario
- Simulated query decomposition for Foundry IQ
- Simulated token usage and timing

## Integration with Azure AI Projects 2.x

**Real Mode Implementation:**

The `agent_client.py` file uses the async `azure-ai-projects` SDK and the OpenAI-compatible Responses API:

1. Create `AIProjectClient` with `DefaultAzureCredential`
2. Acquire an OpenAI-compatible client via `get_openai_client()`
3. Invoke each agent using `responses.create(..., extra_body={"agent_reference": ...})`
4. Convert Responses API output items and streaming events into the demo's `AgentResult` and `TraceEvent` models

**Example Integration:**
```python
async def _execute_real_agent(self, agent_type, question, run_id):
    async with (
      DefaultAzureCredential() as credential,
      AIProjectClient(endpoint=self.project_endpoint, credential=credential) as project_client,
      project_client.get_openai_client() as openai_client,
    ):
      response = await openai_client.responses.create(
        input=question,
        extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
      )
      return self._parse_agent_response(agent_type, agent_name, response, elapsed_ms, run_id)
```

## Development

### Run with Auto-Reload
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Interactive API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing
```bash
# Health check
curl http://localhost:8000/health

# Compare agents
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'
```

## Production Deployment

See [Azure App Service Deployment](../docs/azure-app-service-deployment.md)

**Startup Command:**
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

**Dependencies for Production:**
Add to `requirements.txt`:
```
gunicorn==21.2.0
```

## Error Handling

The backend provides structured error responses:

```json
{
  "detail": "Error message here"
}
```

**Common Errors:**
- `404`: Endpoint or session not found
- `422`: Invalid request body
- `500`: Internal server error (check logs)

## Logging

Logs are printed to stdout/stderr. In production, configure log aggregation (Application Insights, etc.).

**Log Levels:**
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Critical errors

## Performance

**Concurrent Requests:**
- Both agents are called concurrently (`asyncio.gather`)
- WebSocket supports multiple concurrent connections
- No blocking operations in request handlers

**Optimization Tips:**
- Use connection pooling for HTTP clients
- Cache frequent queries (not implemented)
- Scale horizontally for high load

## Security

**CORS:**
- Configured in `main.py`
- Update `allow_origins` for production

**API Keys:**
- Store in environment variables
- Never commit to git
- Use Azure Key Vault in production

**Input Validation:**
- Pydantic models validate all inputs
- Size limits on question text (implicit)

## Troubleshooting

### Import Errors
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Use different port
BACKEND_PORT=8001 python main.py
```

### CORS Errors
Update `allow_origins` in `main.py` to include your frontend URL

### WebSocket Connection Failed
- Check firewall settings
- Verify no proxy blocking WebSocket
- Check browser console for errors

## License

MIT
