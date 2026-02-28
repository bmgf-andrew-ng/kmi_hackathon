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
│       └── (sample page images)           # Blob storage seed data
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

> **Note from Story 58 (Strategy Review MCP verification):** The `azure-storage-blob` 12.28.0 SDK uses API version `2026-02-06` which Azurite 3.33.0 does not support. When implementing this story, add `--skipApiVersionCheck` to the Azurite command in `poc/docker-compose.yml` (e.g. `azurite-blob --blobHost 0.0.0.0 --blobPort 10000 --skipApiVersionCheck`). The `get_page_image` MCP tool in `poc/mcp-servers/strategy-review/strategy_review_mcp/server.py` expects blobs named `{doc_id}/page_{page_num:03d}.png` inside container `strategy-pages`.

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

### Board Summary

| Epic | Name | Features | Stories | Phase |
|------|------|----------|---------|-------|
| **0** | **Project Structure & Scaffolding** | 3 | 10 | **Prerequisite** |
| 1 | Data Tier Infrastructure | 3 | 10 | Phase 1 |
| 2 | MCP Server Integration | 2 | 8 | Phase 1 |
| 3 | Sub-Agents & Strategy Review Skill | 3 | 8 | Phase 1 |
| 4 | Developer Experience (DevContainer) | 1 | 3 | Phase 1 |
| 5 | Additional Review Skills & Polish | 4 | 5 | Phase 2 |
| **Total** | | **16** | **44** | |

### Dependency Graph (with Epic 0)

```
Epic 0 (Structure & Scaffolding)
  │
  ├──→ Epic 1 (Data Tier) → Epic 2 (MCP Servers) → Epic 3 (Agents & Skill) → Epic 5 (More Skills)
  │                                                        │
  └──→ ─────────────────────────────────────────────→ Epic 4 (DevContainer)
```
