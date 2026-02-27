# Architecture Review Toolkit

Tools for reviewing and improving solution architecture designs. Annotate diagrams in the browser, run AI-powered reviews, and get structured improvement plans with local dev recommendations.

## Quick Start

### 1. Annotate your architecture (Playground)

```bash
open architecture-review-playground.html
```

Upload a diagram, draw rectangles around problems, tag components, set severity, add comments. Copy the generated prompt.

### 2. Run the architecture review (Skill)

```
/review-architecture <paste prompt from playground>
```

The `/review-architecture` skill:
- Spawns the `architect-reviewer` sub-agent to evaluate your design
- Assesses against Well-Architected Framework pillars
- Recommends technology stack for every component (production + local dev with Docker)
- Addresses each annotated issue with diagnosis and resolution
- Generates a Mermaid architecture diagram as `{system-name}-architecture.html` and opens it in the browser
- Produces a phased improvement roadmap

### 3. Review the outputs

Each run generates:
- **`{system-name}-architecture.html`** — interactive Mermaid diagram (auto-opens in browser)
- **`{system-name}-review.md`** — full review summary, scorecard, recommendations, and roadmap

### Example

```bash
# 1. Open the playground
open architecture-review-playground.html

# 2. Upload diagram, annotate issues, copy the prompt

# 3. In Claude Code, run:
/review-architecture <paste prompt>

# 4. Review outputs:
#    architecture/my-system-architecture.html  (diagram)
#    architecture/my-system-review.md          (review)
```

## Files

| File | Purpose |
|------|---------|
| `architecture-review-playground.html` | Browser-based diagram annotation tool |
| `*-architecture.html` | Generated Mermaid diagrams from `/review-architecture` |
| `*-review.md` | Generated review summaries from `/review-architecture` |

---

## Playground Features

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

## Playground Workflow

1. **Upload** your architecture diagram (paste, drag, or browse)
2. **Analyze** — click "Analyze Diagram" to get AI-detected components and relationships
3. **Annotate** — draw rectangles around issues, set severity, link to components, add comments
4. **Copy** — grab the generated prompt and run `/review-architecture` in Claude Code

## `/review-architecture` Skill

The skill lives at `.claude/skills/review-architecture/SKILL.md` and uses the `architect-reviewer` sub-agent at `.claude/agents/architect-reviewer.md`.

### What it does

1. Takes the generated prompt from the playground (or any pasted architecture description)
2. Spawns the architect-reviewer agent to perform a full review
3. Presents: summary, Well-Architected scorecard, component tech map, issue resolutions, .devcontainer setup, roadmap
4. Generates `{system-name}-architecture.html` with a Mermaid diagram and opens it in the browser

### Invoking it

```
# With prompt inline
/review-architecture I have a solution architecture for "My System"...

# Empty (will ask you to paste)
/review-architecture
```

### Output files

- `architecture/{system-name}-architecture.html` — Mermaid diagram (dark theme, auto-opens)
- `architecture/{system-name}-review.md` — full review document (create manually or ask Claude)

## Tech

Single HTML file. Zero dependencies. Inline CSS and JS. Dark theme. Works offline (except for the AI analysis step).
