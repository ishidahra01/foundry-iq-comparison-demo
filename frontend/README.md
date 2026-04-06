# Foundry IQ Comparison Demo - Frontend

Next.js frontend for comparing Classic RAG and Foundry IQ agent responses.

## Prerequisites

- Node.js 18+ and npm
- Backend API running (see `/backend/README.md`)

## Getting Started

1. Install dependencies:

```bash
npm install
```

2. Configure environment variables:

```bash
# Create .env.local file
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local
```

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Features

- **Query Input**: Enter questions or select from sample queries
- **Side-by-Side Comparison**: Compare Classic RAG vs Foundry IQ results
- **Processing Timeline**: Visualize execution traces and tool calls
- **Rich Metrics**: View performance, citations, and sources
- **Expandable Sections**: Deep dive into execution details

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles with Tailwind
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Main page component
├── components/
│   ├── AgentResultPanel.tsx # Individual agent result display
│   ├── ComparisonView.tsx   # Main comparison container
│   ├── ProcessingWindow.tsx # Timeline visualization
│   └── QueryInput.tsx       # Query input form
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | `http://localhost:8000` |

## Building for Production

```bash
npm run build
npm start
```

## UI Components

### QueryInput
- Text area for question input
- Sample query selection
- Submit button with loading state

### ComparisonView
- Tabbed interface (Comparison / Timeline)
- Question display with run metadata
- Grid layout for side-by-side agents

### AgentResultPanel
- Answer display with verdict badge
- Performance metrics (time, sources, citations)
- Expandable sections:
  - Answer
  - Citations
  - Execution Details
  - Trace Events

### ProcessingWindow
- Timeline visualization
- Event-by-event trace
- Agent differentiation (color-coded)
- Relative timestamps

## Styling

- **Tailwind CSS** for utility-first styling
- **Custom CSS** for animations and scrollbars
- **Responsive design** with mobile support
- **Light theme** optimized for readability

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Troubleshooting

**Issue: Cannot connect to backend**
- Ensure backend is running on http://localhost:8000
- Check NEXT_PUBLIC_BACKEND_URL environment variable
- Verify CORS settings in backend

**Issue: Sample queries not loading**
- Backend `/sample-queries` endpoint should be accessible
- Check browser console for errors

## License

MIT
