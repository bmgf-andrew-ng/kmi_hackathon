# PoC: Claude Plugin for Accelerating Development

Proof-of-concept validating the end-to-end pattern: **skill → sub-agent → MCP server → data store → synthesised results**.

A three-store RAG architecture where Claude accesses Neo4j (graph), OpenSearch (text), and Azurite (images) through MCP servers, orchestrated by Claude Code skills and sub-agents.

---

## Project Structure

### Under `poc/` — Infrastructure, Data & Application Code

```
poc/
├── plan.md                                  # Implementation plan & ADO board reference
├── create-ado-board.py                      # Azure DevOps work item generator
├── README.md                                # ← You are here
│
├── docker-compose.yml                       # Infrastructure: Neo4j, OpenSearch, Azurite
├── .env.example                             # Template for connection strings
├── .env                                     # Local connection strings (gitignored)
│
├── seed/                                    # Data Layer — seed scripts & data
│   ├── seed-all.sh                          # One-command runner for all stores
│   ├── neo4j/
│   │   ├── seed.cypher                      # Knowledge graph: Documents, Themes,
│   │   │                                    #   Indicators, Countries, FundingAreas
│   │   └── seed.sh                          # Runs cypher-shell against Neo4j container
│   ├── opensearch/
│   │   ├── create-index.sh                  # Index mapping for strategy-chunks
│   │   ├── chunks.ndjson                    # 10-20 representative document chunks
│   │   └── seed.sh                          # Bulk-indexes chunks into OpenSearch
│   └── azurite/
│       ├── seed.sh                          # Uploads page images to Azurite
│       ├── seed.py                          # Python upload script (azure-storage-blob)
│       ├── GH_2024/page_001.png … page_005.png
│       ├── TB_2025/page_001.png … page_003.png
│       └── GE_2023/page_001.png … page_004.png
│
├── mcp-servers/                             # MCP Server Layer — custom servers
│   └── strategy-review/
│       ├── pyproject.toml                   # Python deps: mcp[cli], opensearch-py,
│       │                                    #   azure-storage-blob
│       └── strategy_review_mcp/
│           ├── __init__.py
│           └── server.py                    # FastMCP server exposing:
│                                            #   search_documents(query, top_k)
│                                            #   search_chunks(query, doc_id, top_k)
│                                            #   get_page_image(doc_id, page_num)
│
└── web/                                     # Presentation Layer — Next.js 15 web app
    ├── package.json                         # Dependencies: bedrock-sdk, mcp-sdk, react-markdown
    ├── next.config.ts                       # serverExternalPackages for MCP SDK
    ├── .env.example                         # Template for AWS + data store env vars
    ├── app/
    │   ├── layout.tsx                       # Root layout with dark theme
    │   ├── page.tsx                         # Chat page with skill selector
    │   ├── globals.css                      # Dark GitHub-inspired styles
    │   └── api/chat/route.ts                # Streaming API route with tool use loop
    ├── lib/
    │   ├── mcp-manager.ts                   # MCP server lifecycle + tool routing
    │   └── system-prompts.ts                # Skill system prompts with classification
    ├── components/
    │   ├── chat.tsx                          # Chat container with message list + input
    │   ├── message.tsx                       # Message bubble (react-markdown)
    │   └── skill-selector.tsx                # Strategy / Gender-Tech / Budget picker
    └── sequence-diagram.html                # Interactive Mermaid sequence diagram
```

### At Repo Root

`.devcontainer/` lives at the repo root (required by VS Code):

```
.devcontainer/
├── devcontainer.json                        # Python 3.12, Node 22, port forwarding
├── docker-compose.devcontainer.yml          # Workspace container linked to data tier
├── post-create.sh                           # Post-create setup script
└── seed.sh                                  # Container-aware seed runner
```

### At Repo Root — Claude Code Conventions

These files must live at the repo root per Claude Code's conventions:

```
.claude/
├── agents/                                  # Agent Layer — sub-agent definitions
│   ├── explorer.md                          # (existing) Read-only codebase explorer
│   ├── architect-reviewer.md                # (existing) Solution architecture reviewer
│   ├── graph-traversal.md                   # Neo4j Cypher specialist (Sonnet)
│   ├── document-search.md                   # Text search specialist (Sonnet)
│   └── image-retrieval.md                   # Blob retrieval specialist (Haiku)
├── skills/                                  # Skill Layer — user-facing slash commands
│   ├── greet/SKILL.md                       # (existing) Example greeting skill
│   ├── review-architecture/SKILL.md         # (existing) Architecture review skill
│   ├── strategy-review/SKILL.md             # /strategy-review — graph + text queries
│   ├── gender-tech-review/SKILL.md          # /gender-tech-review — gender equality focus
│   └── budget-review/SKILL.md               # /budget-review — funding & allocation focus
└── settings.local.json                      # (gitignored) Hooks, tokens & MCP env vars

.mcp.json                                   # MCP server registry
                                             #   ado-mcp (docker exec → running container)
                                             #   neo4j (uvx mcp-neo4j-cypher)
                                             #   strategy-review (uv run)
```

---

## Layer Descriptions

| Layer | Location | Purpose | Delivered By |
|-------|----------|---------|-------------|
| **Infrastructure** | `poc/docker-compose.yml`, `poc/.env` | Neo4j 5.26, OpenSearch 2.17, Azurite 3.33 containers | Epic 1: Data Tier Infrastructure |
| **Data/Seed** | `poc/seed/` | Knowledge graph data, document chunks, page images | Epic 1: Data Tier Infrastructure |
| **MCP Servers** | `poc/mcp-servers/`, `.mcp.json` | Custom FastMCP server + Neo4j MCP config | Epic 2: MCP Server Integration |
| **Agents** | `.claude/agents/` | Graph-traversal, document-search, image-retrieval sub-agents | Epic 3: Sub-Agents & Strategy Review Skill |
| **Skills** | `.claude/skills/` | Strategy, gender-tech, budget review slash commands | Epic 3 + Epic 5 |
| **Presentation** | `poc/web/` | Next.js 15 chat UI with streaming Bedrock API + MCP tool use loop | Epic 6: Presentation Layer |
| **DevContainer** | `.devcontainer/` (repo root) | VS Code dev container with all services | Epic 4: Developer Experience |

---

## Component Location Rationale

**Why `poc/` for infrastructure and application code?**
- Isolates the PoC from the learning playground (concept maps, architecture reviews)
- Self-contained: `docker compose up` from `poc/` starts the full data tier
- Reproducible: seed scripts reset data stores to a known state
- Portable: the entire `poc/` folder can be extracted into a standalone repo

**Why repo root for `.claude/` and `.mcp.json`?**
- Claude Code discovers agents from `.claude/agents/*.md` relative to the repo root
- Claude Code discovers skills from `.claude/skills/*/SKILL.md` relative to the repo root
- MCP server registry (`.mcp.json`) must be at the repo root for Claude Code to load it
- These are Claude Code runtime conventions — moving them under `poc/` would break discovery

### Component → Location Mapping

| Component | Location | Constraint | Rationale |
|-----------|----------|-----------|-----------|
| Docker Compose | `poc/docker-compose.yml` | — | Isolates PoC infrastructure from repo root |
| Environment config | `poc/.env` / `poc/.env.example` | — | Scoped to PoC data tier; `.env` gitignored |
| Neo4j seed data | `poc/seed/neo4j/` | — | Co-located with the infrastructure it seeds |
| OpenSearch seed data | `poc/seed/opensearch/` | — | Co-located with the infrastructure it seeds |
| Azurite seed data | `poc/seed/azurite/` | — | Co-located with the infrastructure it seeds |
| Unified seed runner | `poc/seed/seed-all.sh` | — | Orchestrates all seed scripts in one command |
| Strategy Review MCP server | `poc/mcp-servers/strategy-review/` | — | Python application code; isolated package with `pyproject.toml` |
| DevContainer config | `.devcontainer/` (repo root) | — | Binds to `poc/docker-compose.yml` services |
| MCP server registry | `.mcp.json` (repo root) | **Claude Code convention** | Claude Code loads `.mcp.json` from repo root only; cannot be nested |
| graph-traversal agent | `.claude/agents/graph-traversal.md` (repo root) | **Claude Code convention** | Agent discovery requires `.claude/agents/` at repo root |
| document-search agent | `.claude/agents/document-search.md` (repo root) | **Claude Code convention** | Agent discovery requires `.claude/agents/` at repo root |
| image-retrieval agent | `.claude/agents/image-retrieval.md` (repo root) | **Claude Code convention** | Agent discovery requires `.claude/agents/` at repo root |
| strategy-review skill | `.claude/skills/strategy-review/SKILL.md` (repo root) | **Claude Code convention** | Skill discovery requires `.claude/skills/` at repo root |
| gender-tech-review skill | `.claude/skills/gender-tech-review/SKILL.md` (repo root) | **Claude Code convention** | Skill discovery requires `.claude/skills/` at repo root |
| budget-review skill | `.claude/skills/budget-review/SKILL.md` (repo root) | **Claude Code convention** | Skill discovery requires `.claude/skills/` at repo root |
| Claude settings | `.claude/settings.local.json` (repo root) | **Claude Code convention** | Hooks and tokens; gitignored |

---

## Getting Started

Two ways to run the stack — pick whichever suits your workflow.

### Option A: Local Docker (run on host)

Runs the three data-tier services in Docker while you work from your native terminal.

**Prerequisites:** Docker Desktop running, Python 3.10+, `uv` installed.

**1. Create the environment file**

```bash
cp poc/.env.example poc/.env.docker
```

Or use the provided `poc/.env.docker` if it already exists.

**2. Start the data tier**

```bash
cd poc
docker compose --env-file .env.docker up -d
```

**3. Wait for healthy services**

```bash
docker compose ps
```

All three (neo4j, opensearch, azurite) should show `healthy` — takes ~30–60s on first boot.

**4. Seed the data stores**

```bash
bash poc/seed/seed-all.sh        # seeds Neo4j, OpenSearch, and Azurite in one command
```

Or seed individually:

```bash
bash poc/seed/neo4j/seed.sh
bash poc/seed/opensearch/seed.sh
bash poc/seed/azurite/seed.sh
```

**5. Verify services**

```bash
# Neo4j — should return a node count
curl -s -u neo4j:password http://localhost:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{"statements":[{"statement":"MATCH (n) RETURN count(n) AS count"}]}'

# OpenSearch — should return cluster health
curl -s http://localhost:9200/_cluster/health | python3 -m json.tool

# Azurite — should succeed
nc -z localhost 10000 && echo "Azurite is up"
```

**6. Configure Claude Code env vars**

MCP env vars are read from `.claude/settings.local.json` (gitignored). Create it with:

```bash
cat > .claude/settings.local.json << 'EOF'
{
  "env": {
    "NEO4J_URI": "bolt://localhost:7687",
    "NEO4J_USER": "neo4j",
    "NEO4J_PASSWORD": "password",
    "OPENSEARCH_URL": "http://localhost:9200",
    "OPENSEARCH_USER": "admin",
    "OPENSEARCH_PASSWORD": "admin",
    "AZURE_STORAGE_BLOB_ENDPOINT": "http://127.0.0.1:10000/devstoreaccount1",
    "AZURE_STORAGE_CONTAINER": "strategy-pages"
  }
}
EOF
```

> **Note:** Azurite account name and key are well-known constants hardcoded in the
> MCP server — only the blob endpoint needs configuring.

**7. Launch Claude Code**

Open VS Code and the MCP servers will connect automatically using the env vars from `settings.local.json`. Type `/mcp` to verify neo4j and strategy-review tools are visible.

**8. Tear down**

```bash
cd poc
docker compose down        # stops containers, keeps data volumes
docker compose down -v     # stops containers AND deletes data volumes
```

---

### Option B: VS Code DevContainer

Spins up everything inside containers — workspace + data tier — using VS Code's "Reopen in Container".

**Prerequisites:** Docker Desktop running, VS Code with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.

**1. Ensure `poc/.env.docker` exists**

```bash
cp poc/.env.example poc/.env.docker
```

**2. Open the repo in VS Code**

```bash
code /path/to/gf-hackathon
```

**3. Reopen in Container**

`Cmd+Shift+P` → **Dev Containers: Reopen in Container**

VS Code will:
- Pull the Python 3.12 workspace image + data-tier images (first time only)
- Start neo4j, opensearch, azurite and wait for health checks
- Start the workspace container
- Run `.devcontainer/post-create.sh` (installs `uv`, creates venv, installs MCP server)

**4. Seed the data stores** (in the DevContainer terminal)

```bash
bash .devcontainer/seed.sh
```

**5. Verify services** (in the DevContainer terminal)

```bash
# Neo4j
curl -s -u neo4j:password http://neo4j:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{"statements":[{"statement":"MATCH (n) RETURN count(n) AS count"}]}'

# OpenSearch
curl -s http://opensearch:9200/_cluster/health | python3 -m json.tool

# Azurite
nc -z azurite 10000 && echo "Azurite is up"
```

**6. Test MCP servers directly** (in the DevContainer terminal)

```bash
# Strategy Review MCP — list tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  poc/.venv/bin/uv run --directory poc/mcp-servers/strategy-review strategy-review-mcp

# Neo4j MCP — list tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  poc/.venv/bin/uvx mcp-neo4j-cypher
```

If both return JSON with a `tools` array, the MCP servers are working.

**7. Access web UIs from your host browser** (ports are auto-forwarded)

| Service | URL |
|---------|-----|
| Web UI | `http://localhost:3001` (run `cd poc/web && npm run dev` first) |
| Neo4j Browser | `http://localhost:7474` (login: `neo4j` / `password`) |
| OpenSearch API | `http://localhost:9200` |

**8. Return to local dev**

`Cmd+Shift+P` → **Dev Containers: Reopen Folder Locally**

> **Web UI:** Run `cd poc/web && npm run dev` in the DevContainer terminal to start the chat interface on port 3001. See the **E2E Testing** section below for validation steps.

---

### Environment Variables Reference

MCP env vars are set in `.claude/settings.local.json` (local) or `containerEnv` (DevContainer).

| Variable | Local | DevContainer | Used By |
|---|---|---|---|
| `NEO4J_URI` | `bolt://localhost:7687` | `bolt://neo4j:7687` | `.mcp.json` → neo4j MCP |
| `NEO4J_USER` | `neo4j` | `neo4j` | docker-compose, `.mcp.json` |
| `NEO4J_PASSWORD` | `password` | `password` | docker-compose, `.mcp.json` |
| `OPENSEARCH_URL` | `http://localhost:9200` | `http://opensearch:9200` | `.mcp.json` → strategy-review MCP |
| `OPENSEARCH_USER` | `admin` | `admin` | `.mcp.json` → strategy-review MCP |
| `OPENSEARCH_PASSWORD` | `admin` | `admin` | `.mcp.json` → strategy-review MCP |
| `AZURE_STORAGE_BLOB_ENDPOINT` | `http://127.0.0.1:10000/devstoreaccount1` | `http://azurite:10000/devstoreaccount1` | strategy-review MCP (server default) |
| `AZURE_STORAGE_CONTAINER` | `strategy-pages` | `strategy-pages` | strategy-review MCP (server default) |

> **Note:** Azurite account name and key are well-known constants baked into
> every Azurite instance. They are hardcoded in the MCP server — not configurable
> via env vars. Only the blob endpoint differs between local and DevContainer.

The only difference between the two modes is the hostname — `localhost`/`127.0.0.1` for local dev vs Docker service names (`neo4j`, `opensearch`, `azurite`) for DevContainer.

---

## Using the Skills

Once the stack is running and MCP servers are connected, three slash commands are available in Claude Code. Each follows the same pattern: **classify the question → dispatch to graph/text/both agents → synthesise results with citations**.

### `/strategy-review` — General Strategy Analysis

Broad queries across all strategy documents, themes, indicators, countries, and funding areas.

**Try these:**

```
/strategy-review What themes does the Global Health Strategy 2024-2028 cover?
```

> Returns all 7 themes (Maternal & Newborn Health, HIV/AIDS, Malaria, TB, Vaccine Delivery, Digital Health, Gender Equality) with coverage weights from the knowledge graph.

```
/strategy-review Which countries prioritise maternal health and what interventions are recommended?
```

> Dispatches to **both** agents — graph returns priority countries (Nigeria rank 1, India rank 1, Ethiopia rank 2, DR Congo rank 2) while text search returns intervention details from the document corpus. Results are woven together with citations.

```
/strategy-review What does the Global Health Strategy say about malaria prevention?
```

> Dispatches to **text** agent — searches GH_2024 chunks for malaria prevention content, returns summaries with section and page citations.

---

### `/gender-tech-review` — Gender Equality & Women's Health

Focused on the Gender Equality theme, the Gender & Health Equity Framework (GE_2023), GDI/MMR/NMR indicators, and GPE funding.

**Try these:**

```
/gender-tech-review What is the Gender Development Index target and current baseline?
```

> Dispatches to **graph** agent — returns GDI baseline 0.82, target 1.0 by 2028, linked to the Gender Equality & Women's Health theme.

```
/gender-tech-review What does the Gender & Health Equity Framework recommend for reducing maternal mortality?
```

> Dispatches to **text** agent — searches GE_2023 chunks for maternal mortality recommendations, returns policy details with quotes and page citations.

```
/gender-tech-review How is gender equity funding allocated and what programmes does it support?
```

> Dispatches to **both** agents — graph returns GPE allocations ($30M/60% to Gender, $20M/40% to MNH) while text returns programme descriptions from GE_2023. Synthesised into a table with contextual detail.

---

### `/budget-review` — Funding & Budget Analysis

Focused on FundingArea nodes, ALLOCATES_TO relationships, and financial planning across all strategy documents.

**Try these:**

```
/budget-review How is disease prevention funding allocated across themes?
```

> Dispatches to **graph** agent — returns PREV allocations: $90M (45%) to Malaria, $60M (30%) to TB, $50M (25%) to Vaccines. Presented as a financial summary table with totals.

```
/budget-review What is the total budget across all funding areas?
```

> Dispatches to **graph** agent — aggregates all 5 funding areas: HSS $150M, PREV $200M, DIGI $75M, CAPACITY $60M, GPE $50M = **$535M total**.

```
/budget-review What is the rationale behind the digital health investment?
```

> Dispatches to **text** agent — searches for digital health funding rationale across strategy documents, returns justification passages with citations.

---

## Web UI

A Next.js 15 web app that provides the same skill-based analysis through a browser chat interface. The API route handles the tool use loop server-side — spawning MCP servers as child processes, routing tool calls, and streaming the response back via SSE.

### Running the Web UI

**Inside the DevContainer:**

```bash
cd poc/web
npm run dev          # starts on port 3001
```

The app is available at `http://localhost:3001` (port auto-forwarded from the DevContainer).

**On the host (requires data tier running via docker compose):**

```bash
cd poc/web
cp .env.example .env.local
# Edit .env.local with your AWS credentials and localhost URLs
npm install
npm run dev
```

### E2E Testing

These tests validate the full pipeline: Browser → API Route → AWS Bedrock → MCP tool use loop → Data Stores → Streaming response.

**Prerequisites:** Data stores running and seeded, AWS credentials configured, web app running on port 3001.

#### 1. Seed the data stores (if not already done)

```bash
# Neo4j — 33 nodes (3 Documents, 7 Themes, 10 Indicators, 8 Countries, 5 FundingAreas)
docker exec -i <neo4j-container> cypher-shell -u neo4j -p password -d neo4j < poc/seed/neo4j/seed.cypher

# OpenSearch — 15 document chunks across 3 documents
bash poc/seed/opensearch/create-index.sh
curl -sf -X POST "http://localhost:9200/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary "@poc/seed/opensearch/chunks.ndjson"
curl -sf -X POST "http://localhost:9200/strategy-chunks/_refresh"

# Azurite — page images (optional, only needed for get_page_image tool)
bash poc/seed/azurite/seed.sh
```

> **Note:** Replace `<neo4j-container>` with the actual container name — `gf-hackathon_devcontainer-neo4j-1` (DevContainer) or `poc-neo4j-1` (local docker compose).

#### 2. Verify the API endpoint is reachable

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/api/chat \
  -X POST -H "Content-Type: application/json" \
  -d '{"messages":[],"skill":"strategy-review"}'
# Expected: 400 (empty messages validation)
```

#### 3. Strategy Review — Graph query (TB funding)

```bash
curl -s --no-buffer http://localhost:3001/api/chat \
  -X POST -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What funding is allocated to TB?"}],"skill":"strategy-review"}'
```

**Expected behaviour:**
- Claude classifies as **Graph** query
- Calls `neo4j__read_neo4j_cypher` tool (1-3 Cypher queries)
- Returns **PREV → TB allocation: $60M (30%)** of Disease Prevention Programs budget
- Response includes a funding table, Knowledge Graph citations, and follow-up questions
- Stream ends with `data: [DONE]`

#### 4. Gender-Tech Review — Graph query (GDI target)

```bash
curl -s --no-buffer http://localhost:3001/api/chat \
  -X POST -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What is the GDI target?"}],"skill":"gender-tech-review"}'
```

**Expected behaviour:**
- Calls `neo4j__read_neo4j_cypher` tool
- Returns **GDI baseline 0.82, target 1.0 by 2028**
- Mentions GENDER theme and GPE funding area

#### 5. Budget Review — Graph query (total budget)

```bash
curl -s --no-buffer http://localhost:3001/api/chat \
  -X POST -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What is the total budget across all funding areas?"}],"skill":"budget-review"}'
```

**Expected behaviour:**
- Calls `neo4j__read_neo4j_cypher` tool
- Returns **$535M total** across 5 funding areas: HSS $150M, PREV $200M, DIGI $75M, CAPACITY $60M, GPE $50M
- Includes Financial Summary table

#### 6. Strategy Review — Text query (malaria prevention)

```bash
curl -s --no-buffer http://localhost:3001/api/chat \
  -X POST -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What does the Global Health Strategy say about malaria prevention?"}],"skill":"strategy-review"}'
```

**Expected behaviour:**
- Calls `strategy-review__search_documents` and/or `strategy-review__search_chunks`
- Returns text passages from GH_2024 with section and page citations

#### 7. Verify streaming

All of the above should return SSE events incrementally:

```
data: {"type":"text","content":"I"}
data: {"type":"text","content":"'ll search..."}
data: {"type":"text","content":"\n\n*Querying neo4j__read_neo4j_cypher...*\n\n"}
...
data: {"type":"text","content":"## Answer\n..."}
...
data: [DONE]
```

Tool use happens silently server-side — the `*Querying tool_name...*` status messages appear inline so the user knows tools are being called.

---

### How It Works (End-to-End Flow)

```
User types: /strategy-review What funding is allocated to TB elimination?

  1. Skill classifies → Graph (funding query)
  2. Skill dispatches → graph-traversal agent
  3. Agent queries   → Neo4j MCP (mcp__neo4j__read_neo4j_cypher)
  4. Neo4j returns   → FundingArea(PREV)-[:ALLOCATES_TO {$60M, 30%}]->Theme(TB)
  5. Skill synthesises → Formatted answer with citations and follow-up questions
```

### Data Behind the Skills

The three data stores contain:

| Store | Content | Size |
|-------|---------|------|
| **Neo4j** | Knowledge graph: 3 Documents, 7 Themes, 10 Indicators, 8 Countries, 5 Funding Areas + relationships | ~50 nodes, ~40 relationships |
| **OpenSearch** | Document chunks: strategy text passages with metadata (section, page, themes, countries) | 10-20 chunks |
| **Azurite** | Page images: placeholder PNGs for document pages | 12 images across 3 docs |
