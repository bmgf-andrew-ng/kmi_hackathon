# Claude Code Plugin System — Learning Playground

An interactive concept map for learning the Claude Code plugin system through self-paced exploration and iterative prompt-driven learning.

## What's Inside

| File | Purpose |
|------|---------|
| `concept-map.html` | Interactive concept map playground with knowledge tracking |
| `CLAUDE.md` | Project-level memory file (demo: Australian slang) |
| `.claude/skills/greet/SKILL.md` | Example user-invoked skill |
| `.claude/agents/explorer.md` | Read-only codebase explorer subagent |
| `.mcp.json` | GitHub MCP server configuration |
| `.claude/settings.local.json` | Local settings with hooks and env (gitignored) |

## Setup

### 1. Open the Playground

Open `concept-map.html` in any browser — it's a single self-contained file with no dependencies.

### 2. Configure Claude Code (optional hands-on exercises)

Clone this repo and open it in Claude Code to experiment with the included skill, agent, hook, and MCP config:

```bash
git clone https://github.com/bmgf-andrew-ng/kmi_hackathon.git
cd kmi_hackathon
```

Create your local settings file (this is gitignored — your secrets stay safe):

```bash
cat > .claude/settings.local.json << 'EOF'
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Claude finished a response' >> /tmp/claude-log.txt"
          }
        ]
      }
    ]
  },
  "env": {
    "GITHUB_TOKEN": "your_token_here"
  }
}
EOF
```

Then start Claude Code in the project directory to try:
- **CLAUDE.md** loads automatically — Claude will respond in Australian slang
- `/greet Andrew` — triggers the greet skill
- `cat /tmp/claude-log.txt` — see the Stop hook logging after each response

## How to Use the Playground

### Navigating the Map

- **Click** a node to see its description and relationships in the sidebar
- **Drag** nodes to rearrange the layout
- **Scroll** to zoom in/out, **drag** the canvas to pan
- **Double-click** a node to centre it on screen
- Use the **category chips** in the sidebar to filter by type (Core, Extension, Runtime, etc.)
- Press `/` to search for a concept by name
- Press `F` to fit all nodes on screen

### Marking Your Knowledge

The playground has three knowledge levels you cycle through on each concept:

| Level | Symbol | Meaning |
|-------|--------|---------|
| **Know** | ✓ (green) | I understand this concept well |
| **Fuzzy** | ~ (yellow) | I have a rough idea but need clarification |
| **???** | ? (purple) | I don't understand this at all |

To mark a concept:
- **Right-click** any node on the canvas to cycle through levels
- Or **click a node**, then use the knowledge buttons in the sidebar detail panel

The **Knowledge Summary** bar in the sidebar shows your overall progress at a glance.

## Generating Learning Prompts

This is where the iterative learning loop kicks in.

### Step 1: Mark Your Knowledge

Go through each node and honestly mark your understanding level. Don't worry about getting it perfect — the whole point is to iterate.

### Step 2: Generate a Prompt

Press `P` or click the **Prompt** toggle at the bottom of the screen. The playground generates a structured learning prompt based on your markings:

- Concepts you **know** are listed as context anchors
- Concepts you're **fuzzy** on are flagged for clarification with their specific relationships
- Concepts marked **???** are called out as gaps needing explanation from scratch

### Step 3: Copy and Paste into Claude

Click **Copy Prompt** and paste it directly into a Claude Code session (or Claude.ai). Claude will:
- Build on what you already know
- Clarify your fuzzy areas with concrete examples
- Explain unknown concepts from the ground up
- Suggest hands-on exercises to test your understanding

### Step 4: Update Your Markings

After reading Claude's explanation, go back to the playground and update your knowledge levels. Concepts that clicked move from **???** → **Fuzzy** → **Know**.

### Step 5: Repeat

Generate a new prompt with your updated markings. Each iteration focuses on a narrower set of gaps, and the prompt naturally adapts because it reflects your current state.

```
 ┌─────────────────────────────────────┐
 │  Mark knowledge on concept map      │
 │          ↓                          │
 │  Generate prompt (press P)          │
 │          ↓                          │
 │  Copy → Paste into Claude           │
 │          ↓                          │
 │  Read explanation, try exercises    │
 │          ↓                          │
 │  Update markings on concept map     │
 │          ↓                          │
 │  Repeat until all nodes are ✓       │
 └─────────────────────────────────────┘
```

## Concepts Covered

The map covers 17 concepts across 7 categories:

- **Core**: Claude Code
- **Extension**: Plugin, Skill, Subagent, Hook
- **Runtime**: Lifecycle Events, Permissions
- **Distribution**: Marketplace, Plugin Manifest
- **Configuration**: Settings, CLAUDE.md (Memory)
- **Protocol**: MCP Server, LSP Server, Model Context Protocol, Tool
- **User-facing**: Slash Command, Plugin Discovery

Each concept includes a description, its category, and labelled relationship edges showing how it connects to other concepts.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `/` | Search for a concept |
| `Esc` | Clear selection / close search |
| `F` | Fit all nodes on screen |
| `P` | Toggle the prompt panel |
| `1`-`7` | Toggle category filters |
| Right-click | Cycle knowledge level on a node |
