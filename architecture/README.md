# Solution Architecture Review Playground

A self-contained, browser-based tool for reviewing solution architecture diagrams. Upload a screenshot of your architecture, annotate problem areas, link feedback to specific components, and generate a structured review prompt ready to paste into Claude.

## Quick Start

```bash
open architecture-review-playground.html
```

No build step, no dependencies — just open the HTML file in any modern browser.

## Features

### Image Upload
- Drag-and-drop, file picker, or clipboard paste (`Cmd+V` / `Ctrl+V`)
- Supports PNG, JPG, SVG, WebP

### AI-Powered Diagram Analysis
- Sends your diagram to Claude's vision API to identify:
  - **Components** by name and type (service, database, queue, cache, etc.)
  - **Relationships** and data flows between components
  - **Architectural patterns** (microservices, event-driven, CQRS, etc.)
  - **Tech stack** (AWS Lambda, PostgreSQL, Redis, etc.)
- Results displayed in a collapsible "Architecture Overview" panel

### Annotation Drawing
- Click and drag to draw rectangles around problem areas
- Each annotation includes:
  - **Severity** — Critical, Warning, Info, or Suggestion
  - **Linked Components** — tag which AI-detected components the issue relates to
  - **Comment** — free-text description of the problem

### Prompt Generation
- Generates a structured architecture review prompt at the bottom of the page
- Includes the full AI-detected architecture description (components, relationships, patterns)
- Groups annotations by severity with component names and comments
- One-click copy to clipboard — paste straight into Claude

## API Configuration

Click **"Set API Key"** in the top-right to configure your AI provider.

### Anthropic API (Direct)
- Enter your Anthropic API key (`sk-ant-...`)
- Uses `anthropic-dangerous-direct-browser-access` header for browser calls
- Works out of the box with no proxy

### AWS Bedrock
- Enter AWS Access Key ID, Secret Access Key, and optionally a Session Token
- Select your AWS region — the inference profile prefix (`us.`/`eu.`/`ap.`) is added automatically
- **CORS note:** Bedrock doesn't natively allow browser requests. Options:
  - Set a **Proxy Base URL** (e.g. an API Gateway endpoint that forwards to Bedrock)
  - Use a CORS browser extension for local development
- Full SigV4 request signing is implemented in-browser using the Web Crypto API

All credentials are stored in `localStorage` only and never leave your browser except to call the respective API.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `D` | Switch to Draw mode |
| `S` | Switch to Select mode |
| `Cmd+Z` | Undo last annotation |
| `Delete` / `Backspace` | Remove selected annotation |
| `Esc` | Deselect / close modal |

## Workflow

1. **Upload** your architecture diagram (paste, drag, or browse)
2. **Analyze** — click "Analyze Diagram" to get AI-detected components and relationships
3. **Annotate** — draw rectangles around issues, set severity, link to components, add comments
4. **Copy** — grab the generated prompt from the bottom and paste it into Claude for a full architecture redesign

## Tech

Single HTML file. Zero dependencies. Inline CSS and JS. Dark theme. Works offline (except for the AI analysis step).
