# PoC Execution Plan: Claude Plugin for Accelerating Development

## Context

The architecture review (`architecture/claude-plugin-dev-review.md`) identified a three-store RAG architecture that needs: a local dev stack, MCP server integrations, sub-agents, and plugin skills for multiple review topics (Strategy, Gender Tech, Budget). This plan implements the PoC to prove the end-to-end pattern: **skill → sub-agent → MCP server → data store → results**.

Currently the repo has Claude Code config (agents, skills, playground) but zero infrastructure, no data stores, no MCP servers (beyond GitHub), and no application code.

---

## Phase 1 — Data Tier + MCP + First Skill (End-to-End)

### Step 1.1: Docker Compose for data stores
- **Create** `poc/docker-compose.yml` with:
  - `neo4j:5.26-community` (ports 7474, 7687)
  - `opensearchproject/opensearch:2.17.0` (port 9200)
  - `mcr.microsoft.com/azure-storage/azurite:3.33.0` (port 10000)
- **Create** `poc/.env` with connection strings (already gitignored)
- **Verify**: `cd poc && docker compose up -d && docker compose ps` — all healthy

### Step 1.2: Seed Neo4j with strategy knowledge graph
- **Create** `poc/seed/neo4j/seed.cypher` — Documents, Themes, Indicators, Countries, FundingAreas with relationships (COVERS_THEME, MEASURED_BY, PRIORITY_IN, ALLOCATES_TO, SUPPORTS_THEME)
- **Create** `poc/seed/neo4j/seed.sh` — runs cypher-shell against the container
- **Verify**: Neo4j browser at `http://localhost:7474` shows the graph

### Step 1.3: Seed OpenSearch with document chunks
- **Create** `poc/seed/opensearch/create-index.sh` — index mapping for `strategy-chunks`
- **Create** `poc/seed/opensearch/chunks.ndjson` — 10-20 representative document chunks
- **Create** `poc/seed/opensearch/seed.sh` — bulk index the data
- **Verify**: `curl "http://localhost:9200/strategy-chunks/_search?q=maternal+health"` returns hits

### Step 1.4: Configure Neo4j MCP Server
- **Modify** `.mcp.json` — add `neo4j` server using `uvx mcp-neo4j-cypher` (Python package, stdio transport)
  - Exposes tools: `read_neo4j_cypher`, `write_neo4j_cypher`, `get_neo4j_schema`
- **Pre-req**: `uv` installed in `poc/.venv` (`python3 -m venv poc/.venv && poc/.venv/bin/pip install uv`)
- **Verify**: Restart Claude Code, run `/mcp` to confirm tools visible. Ask Claude: "Use the Neo4j MCP to get the database schema"

### Step 1.5: Build Strategy Review MCP Server (Python)
- **Create** `poc/mcp-servers/strategy-review/pyproject.toml` — deps: `mcp[cli]`, `opensearch-py`, `azure-storage-blob`
- **Create** `poc/mcp-servers/strategy-review/strategy_review_mcp/server.py` — FastMCP server with tools:
  - `search_documents(query, top_k)` — BM25 search on OpenSearch
  - `search_chunks(query, doc_id, top_k)` — granular chunk search
  - `get_page_image(doc_id, page_num)` — blob retrieval from Azurite (base64)
- **Modify** `.mcp.json` — add `strategy-review` server using `uv run` (stdio transport)
- **Verify**: Restart Claude Code, test `search_documents` tool with a query

### Step 1.6: Create `graph-traversal` sub-agent
- **Create** `.claude/agents/graph-traversal.md` — Neo4j Cypher specialist
  - Tools: `mcp__neo4j__read_neo4j_cypher`, `mcp__neo4j__get_neo4j_schema`
  - Model: sonnet
- **Verify**: Ask Claude to dispatch to the agent via Task tool and query the graph

### Step 1.7: Create `document-search` sub-agent
- **Create** `.claude/agents/document-search.md` — text search specialist
  - Tools: `mcp__strategy_review__search_documents`, `mcp__strategy_review__search_chunks`
  - Model: sonnet
- **Verify**: Ask Claude to dispatch and search for documents

### Step 1.8: Create `strategy-review` plugin skill
- **Create** `.claude/skills/strategy-review/SKILL.md`
  - Classifies questions as graph/text/combined
  - Dispatches to `graph-traversal` and/or `document-search` agents
  - Synthesises results with source citations
- **Verify** (END-TO-END TEST):
  ```
  /strategy-review What themes does the Global Health Strategy cover?
  ```
  Expected: skill → agent → MCP → Neo4j → results synthesised

### Step 1.9: `.devcontainer` setup
- **Create** `.devcontainer/devcontainer.json` — Python 3.12, Node 22, port forwarding
- **Create** `.devcontainer/docker-compose.devcontainer.yml` — workspace container linked to data tier
- **Verify**: VS Code "Reopen in Container" — all services up, MCP tools available

---

## Phase 2 — Additional Skills + Polish

### Step 2.1: Create `image-retrieval` sub-agent
- `.claude/agents/image-retrieval.md` — uses `get_page_image` tool
- Seed Azurite with sample page images (`poc/seed/azurite/`)

### Step 2.2: Create `gender-tech-review` skill
- `.claude/skills/gender-tech-review/SKILL.md` — clone from strategy-review
- Focus on Theme `gender-equality`, Indicator `gdi`, FundingArea `gpe`

### Step 2.3: Create `budget-review` skill
- `.claude/skills/budget-review/SKILL.md` — clone from strategy-review
- Focus on FundingArea nodes, budget allocations, funding→theme relationships

### Step 2.4: Seed data script
- **Create** `poc/seed/seed-all.sh` — one command to seed all three stores

---

## Dependency Graph

```
1.1 docker-compose
 ├── 1.2 Neo4j seed ──→ 1.4 Neo4j MCP ──→ 1.6 graph-traversal agent ─┐
 ├── 1.3 OpenSearch seed → 1.5 Strategy MCP → 1.7 document-search agent ┤
 └── (Azurite seed) ───────────────────────→ 2.1 image-retrieval agent  │
                                                                         │
                                              1.8 strategy-review skill ←┘
                                                │
                                    ┌───────────┼───────────┐
                                    │           │           │
                                 1.9 devcontainer  2.2 gender  2.3 budget
```

## Execution Order (fastest path to working demo)

| # | Step | Time | What |
|---|------|------|------|
| 1 | 1.1 | 10m | `poc/docker-compose.yml` — data stores up |
| 2 | 1.2 | 15m | Neo4j seed data |
| 3 | 1.4 | 5m | Neo4j MCP in `.mcp.json` |
| 4 | 1.6 | 10m | `graph-traversal` agent |
| 5 | **TEST** | 5m | Ask Claude to query Neo4j via agent — validates pattern |
| 6 | 1.3 | 15m | OpenSearch seed data |
| 7 | 1.5 | 30m | Strategy Review MCP server (Python) |
| 8 | 1.7 | 10m | `document-search` agent |
| 9 | 1.8 | 15m | `strategy-review` skill |
| 10 | **E2E TEST** | 10m | `/strategy-review` full end-to-end |
| 11 | 1.9 | 20m | `.devcontainer` packaging |
| 12 | 2.2-2.3 | 20m | Gender Tech + Budget skills (copy from template) |

**Total: ~3 hours focused implementation**

## Critical Files

| File | Action | Purpose |
|------|--------|---------|
| `poc/docker-compose.yml` | Create | Data tier (Neo4j, OpenSearch, Azurite) |
| `poc/.env` | Create | Connection strings (gitignored) |
| `poc/seed/neo4j/seed.cypher` | Create | Knowledge graph seed data |
| `poc/seed/opensearch/chunks.ndjson` | Create | Document chunk seed data |
| `poc/seed/neo4j/seed.sh` | Create | Neo4j seed runner |
| `poc/seed/opensearch/seed.sh` | Create | OpenSearch seed runner |
| `.mcp.json` | Modify | Add neo4j + strategy-review MCP servers |
| `poc/mcp-servers/strategy-review/` | Create | Custom Python MCP server |
| `.claude/agents/graph-traversal.md` | Create | Neo4j sub-agent |
| `.claude/agents/document-search.md` | Create | Search sub-agent |
| `.claude/skills/strategy-review/SKILL.md` | Create | First review topic skill |
| `.devcontainer/devcontainer.json` | Create | VS Code devcontainer config |
| `.devcontainer/docker-compose.devcontainer.yml` | Create | Devcontainer service |
| `.claude/skills/gender-tech-review/SKILL.md` | Create | Gender Tech skill |
| `.claude/skills/budget-review/SKILL.md` | Create | Budget skill |

## Risks

1. **MCP tools in sub-agents** — Sub-agents may not have access to MCP tools if Claude Code doesn't inject them. Test immediately at step 5. Fallback: skills call MCP tools directly and pass results to agents as context.
2. **`mcp-neo4j-cypher` requires `uvx`** — `uv` is installed inside `poc/.venv` (gitignored). `.mcp.json` references `poc/.venv/bin/uvx`. If venv is missing, recreate with `python3 -m venv poc/.venv && poc/.venv/bin/pip install uv`.
3. **OpenSearch != Azure AI Search** — Query syntax differs. For PoC, code directly against OpenSearch. Production adapter can be added later.

## Verification (End-to-End Test)

After all Phase 1 steps:

```
/strategy-review What themes does the Global Health Strategy 2024-2028 cover and which countries are priorities for maternal health?
```

Expected output: Skill dispatches to both agents. Graph-traversal returns themes and country relationships from Neo4j. Document-search returns supporting text passages from OpenSearch. Skill synthesises into a cited answer mentioning Maternal & Newborn Health, Vaccine Delivery, Digital Health Innovation, and priority countries Nigeria, India, Ethiopia.

---

## Azure DevOps Board — Epics, Features & Stories

### Epic 0: Project Structure & Scaffolding (PREREQUISITE)

*Define and scaffold the to-be project structure for all components and layers under the `poc/` folder before any implementation kicks off.*

#### Feature 0.1: Define Target Folder Structure

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 1 | Design the complete `poc/` directory layout covering all layers: infrastructure, seed data, MCP servers, and devcontainer | Documented structure covers every file/folder from the implementation plan |
| 2 | Document which components live under `poc/` vs repo root (`.claude/` agents & skills, `.mcp.json` must stay at root per Claude Code convention) | Clear mapping of component → location with rationale |

**Target structure:**

```
poc/
├── plan.md                                # (existing) Implementation plan
├── README.md                              # Structure guide & layer descriptions
├── docker-compose.yml                     # Infrastructure: Neo4j, OpenSearch, Azurite
├── .env.example                           # Template for connection strings
│
├── seed/                                  # Data Layer
│   ├── seed-all.sh                        # One-command seed runner
│   ├── neo4j/
│   │   ├── seed.cypher                    # Knowledge graph data
│   │   └── seed.sh                        # Neo4j seed runner
│   ├── opensearch/
│   │   ├── create-index.sh                # Index mapping
│   │   ├── chunks.ndjson                  # Document chunk data
│   │   └── seed.sh                        # OpenSearch seed runner
│   └── azurite/
│       ├── seed.sh                        # Azurite seed runner (bash)
│       ├── seed.py                        # Python upload script (azure-storage-blob)
│       ├── GH_2024/page_001.png … page_005.png
│       ├── TB_2025/page_001.png … page_003.png
│       └── GE_2023/page_001.png … page_004.png
│
├── mcp-servers/                           # MCP Server Layer
│   └── strategy-review/
│       ├── pyproject.toml                 # Python project config
│       └── strategy_review_mcp/
│           ├── __init__.py
│           └── server.py                  # FastMCP server implementation
│
└── (mcp-servers, seed data, docker-compose)

(Repo root)
.devcontainer/                                # Developer Experience Layer
├── devcontainer.json                         # VS Code devcontainer config
├── docker-compose.devcontainer.yml           # Workspace + data tier compose
├── post-create.sh                            # Post-create setup script
└── seed.sh                                   # Container-aware seed runner

.claude/
├── agents/                                # Agent Layer
│   ├── graph-traversal.md                 # Neo4j Cypher specialist
│   ├── document-search.md                 # Text search specialist
│   └── image-retrieval.md                 # Blob retrieval specialist
└── skills/                                # Skill Layer (user-facing)
    ├── strategy-review/SKILL.md
    ├── gender-tech-review/SKILL.md
    └── budget-review/SKILL.md
.mcp.json                                 # MCP server registry
```

#### Feature 0.2: Scaffold Directory Skeleton

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 3 | Create the `poc/seed/neo4j/`, `poc/seed/opensearch/`, `poc/seed/azurite/` directory tree with `.gitkeep` files | All seed directories exist and are tracked by git |
| 4 | Create the `poc/mcp-servers/strategy-review/strategy_review_mcp/` directory tree with `.gitkeep` | MCP server package structure exists |
| 5 | Create the `.devcontainer/` directory at repo root | DevContainer directory exists |
| 6 | Create placeholder directories for future agents and skills under `.claude/` | `.claude/agents/` and `.claude/skills/strategy-review/`, `gender-tech-review/`, `budget-review/` directories exist |

#### Feature 0.3: Foundational Configuration Files

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 7 | Create `poc/README.md` documenting the project structure, layer descriptions, and component responsibilities | README explains each layer, how they connect, and which epic delivers each component |
| 8 | Create `poc/.env.example` with template connection strings for Neo4j, OpenSearch, and Azurite | All required env vars listed with placeholder values and comments |
| 9 | Update `.gitignore` with `poc/`-specific patterns (`.env`, data volumes, Python venvs, `__pycache__`) | Sensitive files and build artefacts under `poc/` are excluded from git |
| 10 | Update `plan.md` with finalised file paths reflecting the `poc/`-scoped structure | All file paths in the plan match the agreed directory layout |

---

### Epic 1: Data Tier Infrastructure

*Stand up the foundational data stores and seed them with representative data.*

#### Feature 1.1: Docker Compose Data Stores

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 11 | Create `docker-compose.yml` with Neo4j 5.26, OpenSearch 2.17, and Azurite 3.33 | Ports 7474/7687, 9200, 10000 exposed |
| 12 | Create `.env` file with connection strings (gitignored) | File exists, not tracked by git |
| 13 | Verify all containers start healthy | `docker compose up -d && docker compose ps` — all show healthy |

#### Feature 1.2: Neo4j Knowledge Graph Seeding

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 14 | Create `seed/neo4j/seed.cypher` with Documents, Themes, Indicators, Countries, FundingAreas and relationships | Cypher file creates nodes with COVERS_THEME, MEASURED_BY, PRIORITY_IN, ALLOCATES_TO, SUPPORTS_THEME relationships |
| 15 | Create `seed/neo4j/seed.sh` runner script | Script executes cypher-shell against the Neo4j container |
| 16 | Verify knowledge graph in Neo4j browser | `http://localhost:7474` shows the graph with all node types and relationships |

#### Feature 1.3: OpenSearch Document Chunk Seeding

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 17 | Create `seed/opensearch/create-index.sh` with index mapping for `strategy-chunks` | Index mapping created with appropriate fields |
| 18 | Create `seed/opensearch/chunks.ndjson` with 10-20 representative document chunks | NDJSON file with realistic strategy document content |
| 19 | Create `seed/opensearch/seed.sh` for bulk indexing | Script bulk-indexes chunks into OpenSearch |
| 20 | Verify document search works | `curl` query for "maternal health" returns hits |

---

### Epic 2: MCP Server Integration

*Wire up MCP servers so Claude Code can talk to the data stores.*

#### Feature 2.1: Neo4j MCP Server Configuration

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 21 | Add `neo4j` server to `.mcp.json` using `uvx mcp-neo4j-cypher` | Config uses stdio transport, exposes `read_neo4j_cypher`, `write_neo4j_cypher`, `get_neo4j_schema` |
| 22 | Verify Neo4j MCP tools visible in Claude Code | `/mcp` shows neo4j tools; Claude can get the DB schema |

#### Feature 2.2: Strategy Review MCP Server (Custom Python)

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 23 | Create `mcp-servers/strategy-review/pyproject.toml` with deps (`mcp[cli]`, `opensearch-py`, `azure-storage-blob`) | Project builds with `uv` |
| 24 | Implement `search_documents(query, top_k)` tool — BM25 search on OpenSearch | Returns ranked document results |
| 25 | Implement `search_chunks(query, doc_id, top_k)` tool — granular chunk search | Returns chunk-level results filtered by doc_id |
| 26 | Implement `get_page_image(doc_id, page_num)` tool — blob retrieval from Azurite | Returns base64-encoded page image |
| 27 | Add `strategy-review` server to `.mcp.json` using `uv run` (stdio transport) | Server registered in MCP config |
| 28 | Verify `search_documents` tool works end-to-end | Claude can invoke tool and get search results |

---

### Epic 3: Sub-Agents & Strategy Review Skill

*Build the intelligent layer — sub-agents that specialise in graph traversal and text search, orchestrated by the strategy-review skill.*

#### Feature 3.1: Graph Traversal Sub-Agent

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 29 | Create `.claude/agents/graph-traversal.md` — Neo4j Cypher specialist (Sonnet model) | Agent has access to `mcp__neo4j__read_neo4j_cypher` and `mcp__neo4j__get_neo4j_schema` |
| 30 | Verify agent can query Neo4j via Task tool dispatch | Claude dispatches to agent and returns graph query results |

#### Feature 3.2: Document Search Sub-Agent

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 31 | Create `.claude/agents/document-search.md` — text search specialist (Sonnet model) | Agent has access to `mcp__strategy_review__search_documents` and `search_chunks` |
| 32 | Verify agent can search and return documents | Claude dispatches to agent and returns search results |

#### Feature 3.3: Strategy Review Skill (End-to-End Orchestration)

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 33 | Create `.claude/skills/strategy-review/SKILL.md` with question classification logic | Skill classifies questions as graph/text/combined |
| 34 | Implement agent dispatch — routes to graph-traversal and/or document-search | Correct agent(s) invoked based on question type |
| 35 | Implement result synthesis with source citations | Answer cites both graph and text sources |
| 36 | **End-to-end test**: `/strategy-review What themes does the Global Health Strategy cover?` | Skill → Agent → MCP → Data Store → Synthesised answer |

---

### Epic 4: Developer Experience (DevContainer)

*Package the whole stack so any dev can spin it up in VS Code.*

#### Feature 4.1: DevContainer Setup

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 37 | Create `.devcontainer/devcontainer.json` with Python 3.12, Node 22, port forwarding | Config specifies correct base image and forwarded ports |
| 38 | Create `.devcontainer/docker-compose.devcontainer.yml` linking workspace to data tier | Workspace container can reach Neo4j, OpenSearch, Azurite |
| 39 | Verify "Reopen in Container" works | All services up, MCP tools available inside container |

---

### Epic 5: Additional Review Skills & Polish

*Extend the pattern to Gender Tech and Budget review domains.*

#### Feature 5.1: Image Retrieval Sub-Agent

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 40 | Create `.claude/agents/image-retrieval.md` using `get_page_image` tool | Agent can retrieve and return page images |
| 41 | Seed Azurite with sample page images in `seed/azurite/` | Images accessible via blob storage |

> **Implementation notes (completed):**
> - `--skipApiVersionCheck` added to the Azurite command in `poc/docker-compose.yml` to handle `azure-storage-blob` 12.28.0 API version `2026-02-06` that Azurite 3.33.0 does not natively support.
> - Azurite well-known dev credentials (account name `devstoreaccount1` and key) are hardcoded in `server.py` — only `AZURE_STORAGE_BLOB_ENDPOINT` and `AZURE_STORAGE_CONTAINER` are configurable via env vars (with sensible defaults). This avoids env var substitution issues with special characters in the base64 key.
> - Seed data: 12 placeholder PNG images across 3 docs (`GH_2024/`, `TB_2025/`, `GE_2023/`), uploaded by `poc/seed/azurite/seed.py` using the Azure SDK.
> - The `get_page_image` MCP tool expects blobs named `{doc_id}/page_{page_num:03d}.png` inside container `strategy-pages`.

#### Feature 5.2: Gender Tech Review Skill

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 42 | Create `.claude/skills/gender-tech-review/SKILL.md` (cloned from strategy-review) | Focuses on Theme `gender-equality`, Indicator `gdi`, FundingArea `gpe` |

#### Feature 5.3: Budget Review Skill

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 43 | Create `.claude/skills/budget-review/SKILL.md` (cloned from strategy-review) | Focuses on FundingArea nodes, budget allocations, funding→theme relationships |

#### Feature 5.4: Unified Seed Script

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 44 | Create `seed/seed-all.sh` — one command to seed all three stores | Single script seeds Neo4j, OpenSearch, and Azurite |

---

## Phase 3 — Presentation Layer (Web UI)

### Decisions

- **Auth**: Skip entirely for PoC (no Keycloak, no API key check). Phase 2 concern.
- **Model**: Claude Sonnet via AWS Bedrock (`us.anthropic.claude-sonnet-4-20250514-v1:0`).
- **API provider**: AWS Bedrock (not direct Anthropic API). Auth via `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` + `AWS_REGION` env vars.
- **Dev model**: DevContainer-first — optimise for zero-setup sharing across developers.
- **Claude Code CLI in devcontainer**: Yes — with `CLAUDE_CODE_USE_BEDROCK=1`.
- **Playground plugin**: Not suitable — tool use loop requires server-side backend (MCP servers use stdio transport, data stores have CORS restrictions, API keys would be exposed in browser).

### Architecture

```
Browser → Next.js API Route → AWS Bedrock (Claude Sonnet, streaming)
                                    ↕ tool_use / tool_result
                              MCP Client Manager
                              ├── strategy-review MCP (stdio) → OpenSearch + Azurite
                              └── neo4j MCP (stdio) → Neo4j
```

The `@modelcontextprotocol/sdk` Client class spawns existing MCP servers as child processes — zero code duplication, dynamic tool discovery via `client.listTools()`, same tool signatures.

### Sequence Diagram

> Open [`poc/web/sequence-diagram.html`](web/sequence-diagram.html) in a browser to view the interactive diagram.

**Key flows:**

1. **First request** — MCP Manager spawns both MCP servers as child processes, discovers 6 tools
2. **Every request** — API route selects system prompt by skill, sends to Bedrock with tool definitions
3. **Tool use loop** — Bedrock returns `tool_use` blocks, API route calls MCP servers which hit data stores, returns `tool_result`, Bedrock continues
4. **Streaming** — Text tokens flow back to the browser via SSE as they arrive
5. **Shutdown** — `SIGTERM`/`SIGINT` triggers graceful cleanup of MCP child processes

### DevContainer-First Development Model

```
Host Machine
├── VS Code → "Reopen in Container"
└── Docker Desktop
    ├── workspace (devcontainer)
    │   ├── VS Code Server + terminal
    │   ├── Node.js 22 (npm run dev → port 3001, auto-forwarded)
    │   │   └── MCP servers (child procs → Docker service names)
    │   ├── Python 3.12 + uv (MCP server deps)
    │   ├── Claude Code CLI (skills/agents dev)
    │   └── AWS CLI credentials via env vars
    ├── neo4j (:7474, :7687)
    ├── opensearch (:9200)
    └── azurite (:10000)
```

### Target Structure

```
poc/web/
├── package.json
├── tsconfig.json
├── next.config.ts
├── .env.local              # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, data store URLs
├── app/
│   ├── layout.tsx          # Root layout, dark theme, global styles
│   ├── page.tsx            # Chat UI page
│   ├── globals.css         # Dark GitHub-inspired theme
│   └── api/
│       └── chat/
│           └── route.ts    # Streaming API route (POST)
├── lib/
│   ├── mcp-manager.ts      # MCP server lifecycle + tool routing
│   └── system-prompts.ts   # Skill system prompts (from SKILL.md files)
└── components/
    ├── chat.tsx             # Chat container with message list + input
    ├── message.tsx          # Message bubble (markdown rendering)
    └── skill-selector.tsx   # Strategy / Gender-Tech / Budget selector
```

---

### Epic 6: Presentation Layer (Web UI)

*Add a Next.js 15 web app so non-technical users can query strategies, budgets, and gender-tech data through a browser — powered by AWS Bedrock + existing MCP servers.*

**Depends on:** Epic 2 (MCP Servers) + Epic 3 (Agents & Skills) + Epic 4 (DevContainer)

#### Feature 6.1: Next.js App Scaffolding

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 45 | Scaffold Next.js 15 app with App Router + TypeScript in `poc/web/` | `npx create-next-app` generates working app at `poc/web/`, `npm run dev` starts on port 3001 |
| 46 | Add project dependencies: `@anthropic-ai/sdk`, `@modelcontextprotocol/sdk`, `react-markdown`, `remark-gfm` | All deps in `package.json`, `npm install` succeeds |
| 47 | Create `.env.local` template with AWS Bedrock credentials and data store URLs | Template file documents all required env vars; `.env.local` is gitignored |

#### Feature 6.2: MCP Client Manager

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 48 | Implement `lib/mcp-manager.ts` singleton that spawns strategy-review and neo4j MCP servers as child processes via `StdioClientTransport` | MCP servers start on first request, singleton prevents duplicate processes |
| 49 | Implement dynamic tool discovery — `client.listTools()` at startup extracts tool definitions for the Anthropic API | Tools `search_documents`, `search_chunks`, `get_page_image`, `read_neo4j_cypher` discovered and formatted as Anthropic tool schemas |
| 50 | Implement `callTool(serverName, toolName, args)` routing and graceful shutdown on process exit | Tool calls routed to correct MCP server; servers cleaned up on `SIGTERM`/`SIGINT` |

#### Feature 6.3: System Prompts & Skill Integration

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 51 | Create `lib/system-prompts.ts` with strategy-review system prompt extracted from `.claude/skills/strategy-review/SKILL.md` | Prompt includes graph schema, document corpus, classification logic, and synthesis output format |
| 52 | Add gender-tech-review system prompt variant (gender equality & women's health lens) | Prompt focuses on GDI indicator, GPE funding, GE_2023 framework |
| 53 | Add budget-review system prompt variant (funding allocations & budget breakdowns) | Prompt focuses on FundingArea nodes, allocation percentages, $535M total budget |

#### Feature 6.4: Streaming API Route with Tool Use Loop

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 54 | Implement `app/api/chat/route.ts` POST handler with `AnthropicBedrock` client (`us.anthropic.claude-sonnet-4-20250514-v1:0`) | Route accepts `{ messages, skill }`, selects system prompt, returns streaming response |
| 55 | Implement server-side tool use loop — on `tool_use` block, call `mcpManager.callTool()`, return `tool_result`, resume | Claude queries Neo4j/OpenSearch via MCP tools transparently; loop handles multiple tool calls per turn |
| 56 | Implement streaming response via `ReadableStream` with `Content-Type: text/event-stream` | Text tokens stream to client as they arrive; tool use happens silently server-side |
| 57 | **End-to-end test**: POST to `/api/chat` with "What funding is allocated to TB?" | Returns streaming response with funding data from Neo4j graph ($60M PREV→TB) |

#### Feature 6.5: Chat UI

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 58 | Build `components/skill-selector.tsx` — three buttons/tabs: Strategy Review, Gender-Tech, Budget | Selected skill highlighted; selection passed to API route |
| 59 | Build `components/chat.tsx` — chat container with scrollable message list and text input | Messages display in order; input clears on send; auto-scroll to latest |
| 60 | Build `components/message.tsx` — message bubble with markdown rendering (tables, citations, block quotes) | `react-markdown` + `remark-gfm` renders tables, inline citations, and block quotes correctly |
| 61 | Implement streaming display — tokens appear incrementally as they arrive from SSE | User sees text building up word-by-word, not all at once |
| 62 | Apply dark GitHub-inspired theme matching existing playground styling | Dark background (#0d1117), light text (#c9d1d9), consistent with `architecture-review-playground.html` |

#### Feature 6.6: DevContainer Integration

| # | Story | Acceptance Criteria |
|---|-------|-------------------|
| 63 | Update `.devcontainer/devcontainer.json` — add port 3001 forwarding, AWS credentials to `containerEnv`, `CLAUDE_CODE_USE_BEDROCK=1` | Port 3001 labelled "Web UI"; AWS env vars available inside container |
| 64 | Update `.devcontainer/post-create.sh` — install Claude Code CLI (`npm install -g @anthropic-ai/claude-code`) and web app deps (`cd poc/web && npm install`) | Both installs succeed in post-create; `claude --version` and `npm run dev` work inside container |
| 65 | **Verification**: Rebuild devcontainer, seed data, start web app on port 3001 | "Reopen in Container" → data stores healthy → `npm run dev` → http://localhost:3001 loads |
| 66 | **Verification**: Claude Code CLI works with Bedrock inside devcontainer | `claude` command launches, MCP tools (`/mcp`) visible, skills (`/strategy-review`) functional |

---

### Files to Create (Phase 3)

| File | Purpose |
|------|---------|
| `poc/web/package.json` | Next.js 15 + deps |
| `poc/web/tsconfig.json` | TypeScript config |
| `poc/web/next.config.ts` | Next.js config |
| `poc/web/.env.local` | AWS credentials + data store URLs (gitignored) |
| `poc/web/app/layout.tsx` | Root layout + dark theme |
| `poc/web/app/page.tsx` | Chat page |
| `poc/web/app/globals.css` | Dark GitHub-inspired styles |
| `poc/web/app/api/chat/route.ts` | Streaming API route + tool use loop |
| `poc/web/lib/mcp-manager.ts` | MCP server lifecycle + tool routing |
| `poc/web/lib/system-prompts.ts` | Skill system prompts |
| `poc/web/components/chat.tsx` | Chat container |
| `poc/web/components/message.tsx` | Message rendering (markdown) |
| `poc/web/components/skill-selector.tsx` | Skill picker |

### Files to Modify (Phase 3)

| File | Change |
|------|--------|
| `.devcontainer/devcontainer.json` | Add port 3001, AWS creds, CLAUDE_CODE_USE_BEDROCK |
| `.devcontainer/post-create.sh` | Install Claude Code CLI + web app npm deps |

### Verification (Phase 3 — inside devcontainer)

1. **Rebuild devcontainer**: VS Code → "Rebuild Container" — verify all services start (Neo4j 7474, OpenSearch 9200, Azurite 10000)
2. **Seed data**: `bash .devcontainer/seed.sh` — verify data in all three stores
3. **Web app starts**: `cd poc/web && npm run dev` — verify http://localhost:3001 loads (auto-forwarded)
4. **MCP servers connect**: Check terminal output — strategy-review and neo4j MCP servers spawn on first request
5. **Strategy review**: Ask "What funding is allocated to TB?" — expect graph data with funding amounts from Neo4j
6. **Gender-tech review**: Ask "What is the GDI target?" — expect GDI baseline 0.82, target 1.0
7. **Budget review**: Ask "How is prevention funding allocated?" — expect PREV $200M breakdown with table
8. **Streaming**: Verify tokens appear incrementally (not all at once) in the chat UI
9. **Claude Code CLI**: Run `claude` in devcontainer terminal — verify skills and MCP tools work via Bedrock

---

### Board Summary

| Epic | Name | Features | Stories | Phase |
|------|------|----------|---------|-------|
| **0** | **Project Structure & Scaffolding** | 3 | 10 | **Prerequisite** |
| 1 | Data Tier Infrastructure | 3 | 10 | Phase 1 |
| 2 | MCP Server Integration | 2 | 8 | Phase 1 |
| 3 | Sub-Agents & Strategy Review Skill | 3 | 8 | Phase 1 |
| 4 | Developer Experience (DevContainer) | 1 | 3 | Phase 1 |
| 5 | Additional Review Skills & Polish | 4 | 5 | Phase 2 |
| **6** | **Presentation Layer (Web UI)** | **6** | **22** | **Phase 3** |
| **Total** | | **22** | **66** | |

### Dependency Graph (with Epic 0)

```
Epic 0 (Structure & Scaffolding)
  │
  ├──→ Epic 1 (Data Tier) → Epic 2 (MCP Servers) → Epic 3 (Agents & Skill) → Epic 5 (More Skills)
  │                                │                       │
  │                                └───────────────────────┤
  │                                                        ↓
  └──→ ──────────────────────────────────────────→ Epic 4 (DevContainer)
                                                           │
                                    Epic 2 + Epic 3 + Epic 4
                                                           ↓
                                                   Epic 6 (Web UI)
```
