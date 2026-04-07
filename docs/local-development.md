# Local Development Guide

This guide covers setting up and running the Foundry IQ Comparison Demo locally for development.

## Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Git**
- Code editor (VS Code recommended)

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ishidahra01/foundry-iq-comparison-demo.git
cd foundry-iq-comparison-demo
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

```bash
# Copy example environment file
cp ../.env.example ../.env

# Edit .env with your settings (or leave as-is for mock mode)
```

For **mock mode** (no Azure required):
```bash
# Just leave MOCK_MODE unset or explicitly set to true
MOCK_MODE=true
```

For **real Azure integration**:
```bash
AZURE_AI_PROJECT_ENDPOINT=https://your-ai-services-account.services.ai.azure.com/api/projects/your-project-name
CLASSIC_RAG_AGENT_NAME=classic-rag-agent
FOUNDRY_IQ_AGENT_NAME=foundry-iq-agent
MOCK_MODE=false
```

Real mode uses `DefaultAzureCredential`. Run `az login` locally, or configure a managed identity in Azure.

#### Run Backend

```bash
# Simple start
python main.py

# Or with uvicorn for auto-reload (recommended for development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at **http://localhost:8000**

Verify it's running:
```bash
curl http://localhost:8000/health
```

### 3. Frontend Setup

Open a **new terminal** (keep backend running):

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at **http://localhost:3000**

Open http://localhost:3000 in your browser.

## Development Workflow

### Backend Development

#### File Structure
```
backend/
├── main.py              # FastAPI app and endpoints
├── models.py            # Pydantic data models
├── agent_client.py      # Foundry Agent client
├── mock_responses.py    # Mock data generator
└── requirements.txt     # Dependencies
```

#### Hot Reload

When running with `uvicorn --reload`, the server automatically restarts when you modify Python files.

#### API Testing

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Comparison Endpoint:**
```bash
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the project timeline?"}'
```

**Sample Queries:**
```bash
curl http://localhost:8000/sample-queries
```

#### Interactive API Docs

FastAPI provides automatic API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Development

#### File Structure
```
frontend/
├── app/
│   ├── page.tsx          # Main page
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles
├── components/
│   ├── QueryInput.tsx    # Query input form
│   ├── ComparisonView.tsx # Main comparison UI
│   ├── AgentResultPanel.tsx # Agent result display
│   └── ProcessingWindow.tsx # Timeline view
└── package.json
```

#### Hot Reload

Next.js automatically reloads when you modify files. Changes appear instantly in the browser.

#### Component Development

To work on a specific component:

1. Open the component file in `components/`
2. Modify the code
3. Save - browser auto-updates
4. Use React DevTools for debugging

#### Styling

This project uses **Tailwind CSS**:

```tsx
// Example: Add a blue background
<div className="bg-blue-500 text-white p-4 rounded">
  Hello World
</div>
```

See [Tailwind docs](https://tailwindcss.com/docs) for utility classes.

#### TypeScript

The project is fully typed with TypeScript. The compiler will show errors in your editor and during build.

Check types manually:
```bash
npm run build  # This includes type checking
```

## Testing

### Backend Testing

**Manual API Testing:**
```bash
# In Python
python
>>> import requests
>>> response = requests.post(
...     "http://localhost:8000/compare",
...     json={"question": "Test question"}
... )
>>> print(response.json())
```

**Mock Mode Verification:**

Ensure mock responses are working:
```bash
# Should see "Running in MOCK MODE" in backend logs
python main.py
```

### Frontend Testing

**Browser Testing:**
1. Open http://localhost:3000
2. Click "Sample Queries"
3. Select a query
4. Click "Compare Agents"
5. Verify both panels show results

**Console Debugging:**

Open browser console (F12) to see:
- Network requests
- React component rendering
- JavaScript errors

## Common Development Tasks

### Adding a New Backend Endpoint

1. Open `backend/main.py`
2. Add your endpoint:
```python
@app.get("/my-endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```
3. Test: `curl http://localhost:8000/my-endpoint`

### Adding a New Frontend Component

1. Create `frontend/components/MyComponent.tsx`:
```tsx
"use client";

export default function MyComponent() {
  return <div>My Component</div>;
}
```

2. Import and use in `app/page.tsx`:
```tsx
import MyComponent from "@/components/MyComponent";

// Use in JSX
<MyComponent />
```

### Modifying Mock Responses

Edit `backend/mock_responses.py`:

```python
def _generate_classic_rag_response(self, question, run_id):
    answer = "Your custom mock answer here"
    # ... rest of the response
```

### Changing UI Styles

Edit `frontend/app/globals.css` for global styles or use Tailwind classes inline.

## Environment Variables

### Backend (.env)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AZURE_AI_PROJECT_ENDPOINT` | Azure AI Project endpoint | - | No (mock mode) |
| `CLASSIC_RAG_AGENT_NAME` | Classic agent name | `classic-rag-agent` | No |
| `FOUNDRY_IQ_AGENT_NAME` | Foundry IQ agent name | `foundry-iq-agent` | No |
| `MOCK_MODE` | Enable mock responses | `true` if no Azure config | No |
| `BACKEND_HOST` | Host to bind | `0.0.0.0` | No |
| `BACKEND_PORT` | Port to bind | `8000` | No |

### Frontend (.env.local)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | `http://localhost:8000` |

**Note:** Next.js variables must be prefixed with `NEXT_PUBLIC_` to be accessible in browser.

## Debugging

### Backend Debugging

**Print Debugging:**
```python
print(f"Debug: {variable}")
```

**Python Debugger:**
```python
import pdb; pdb.set_trace()  # Breakpoint
```

**VS Code Debugging:**

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

### Frontend Debugging

**Console Logging:**
```tsx
console.log("Debug:", data);
```

**React DevTools:**

Install browser extension:
- [Chrome](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
- [Firefox](https://addons.mozilla.org/en-US/firefox/addon/react-devtools/)

**VS Code Debugging:**

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug client-side",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000"
    }
  ]
}
```

## Performance Optimization

### Backend

**Profile API calls:**
```python
import time

start = time.time()
# ... code to profile
print(f"Elapsed: {time.time() - start}s")
```

**Monitor resource usage:**
```bash
# CPU and memory
htop

# Or simpler
top
```

### Frontend

**React DevTools Profiler:**
1. Open React DevTools
2. Click "Profiler" tab
3. Record interactions
4. Analyze render times

**Lighthouse:**
1. Open Chrome DevTools
2. Go to "Lighthouse" tab
3. Run audit
4. Review performance score

## Code Quality

### Backend (Python)

**Format code:**
```bash
# Install black
pip install black

# Format
black backend/
```

**Lint code:**
```bash
# Install flake8
pip install flake8

# Lint
flake8 backend/
```

### Frontend (TypeScript/React)

**Lint:**
```bash
npm run lint
```

**Format (if Prettier configured):**
```bash
npx prettier --write .
```

## Troubleshooting

### Port Already in Use

**Backend (8000):**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

**Frontend (3000):**
```bash
# Same process, just use port 3000
lsof -i :3000
```

### Module Not Found

**Backend:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Frontend:**
```bash
# Delete and reinstall
rm -rf node_modules package-lock.json
npm install
```

### CORS Errors

If you see CORS errors in browser console:

1. Check backend CORS configuration in `main.py`
2. Ensure frontend URL is in `allow_origins`
3. Restart backend after changes

### TypeScript Errors

```bash
# Check for type errors
cd frontend
npm run build
```

Fix errors shown in output.

## Git Workflow

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add my feature"

# Push to remote
git push origin feature/my-feature

# Create pull request on GitHub
```

### Commit Messages

Follow conventional commits:
- `feat: Add new component`
- `fix: Resolve CORS issue`
- `docs: Update README`
- `refactor: Simplify agent client`
- `test: Add unit tests`

## Next Steps

- Review [Azure AI Search Setup](azure-ai-search-setup.md) for production data
- Review [Foundry IQ Setup](foundry-iq-setup.md) for knowledge base
- Review [Foundry Agent Setup](foundry-agent-setup.md) for agent configuration
- Deploy to [Azure App Service](azure-app-service-deployment.md)

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
