#!/usr/bin/env python3
"""Create Azure DevOps work items for the PoC implementation plan."""

import json
import urllib.request
import sys

MCP_URL = "http://localhost:3000/mcp"
PROJECT = "PoC playground"
REQUEST_ID = 0


def call_mcp(tool_name: str, arguments: dict) -> dict:
    """Call an MCP tool and return the parsed result."""
    global REQUEST_ID
    REQUEST_ID += 1
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": REQUEST_ID,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }).encode()
    req = urllib.request.Request(MCP_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    text = data["result"]["content"][0]["text"]
    return json.loads(text)


def create_epic(title: str, description: str, priority: int, tags: list[str], value_area: str = "Business") -> int:
    result = call_mcp("create_epic", {
        "project": PROJECT,
        "title": title,
        "description": description,
        "priority": priority,
        "tags": tags,
        "valueArea": value_area,
    })
    print(f"  Epic #{result['id']}: {title}")
    return result["id"]


def create_feature(title: str, description: str, parent_id: int, priority: int, tags: list[str], value_area: str = "Business") -> int:
    result = call_mcp("create_feature", {
        "project": PROJECT,
        "title": title,
        "description": description,
        "parentId": parent_id,
        "priority": priority,
        "tags": tags,
        "valueArea": value_area,
    })
    print(f"    Feature #{result['id']}: {title}")
    return result["id"]


def create_story(title: str, description: str, acceptance_criteria: str, parent_id: int, priority: int, tags: list[str]) -> int:
    result = call_mcp("create_user_story", {
        "project": PROJECT,
        "title": title,
        "description": description,
        "acceptanceCriteria": acceptance_criteria,
        "parentId": parent_id,
        "priority": priority,
        "tags": tags,
    })
    print(f"      Story #{result['id']}: {title}")
    return result["id"]


def main():
    print("=" * 60)
    print("Creating Azure DevOps Board — PoC Implementation Plan")
    print("=" * 60)

    # ── Epic 0 already exists (ID 9) ──
    epic0_id = 9
    print(f"\n  Epic #{epic0_id}: Epic 0: Project Structure & Scaffolding (already exists)")

    # ── Create remaining Epics ──
    print("\n── Creating Epics ──")

    epic1_id = create_epic(
        "Epic 1: Data Tier Infrastructure",
        "<p>Stand up the foundational data stores and seed them with representative data.</p>"
        "<p><strong>Phase:</strong> Phase 1 | <strong>Features:</strong> 3 | <strong>Stories:</strong> 10</p>"
        "<p><strong>Dependency:</strong> Requires Epic 0 (Project Structure) to be complete.</p>",
        priority=1, tags=["PoC", "Phase-1", "Infrastructure"], value_area="Architectural",
    )

    epic2_id = create_epic(
        "Epic 2: MCP Server Integration",
        "<p>Wire up MCP servers so Claude Code can talk to the data stores.</p>"
        "<p><strong>Phase:</strong> Phase 1 | <strong>Features:</strong> 2 | <strong>Stories:</strong> 8</p>"
        "<p><strong>Dependency:</strong> Requires Epic 1 (Data Tier) to be complete.</p>",
        priority=1, tags=["PoC", "Phase-1", "MCP"],
    )

    epic3_id = create_epic(
        "Epic 3: Sub-Agents & Strategy Review Skill",
        "<p>Build the intelligent layer — sub-agents that specialise in graph traversal and text search, orchestrated by the strategy-review skill.</p>"
        "<p><strong>Phase:</strong> Phase 1 | <strong>Features:</strong> 3 | <strong>Stories:</strong> 8</p>"
        "<p><strong>Dependency:</strong> Requires Epic 2 (MCP Servers) to be complete.</p>",
        priority=1, tags=["PoC", "Phase-1", "Agents", "Skills"],
    )

    epic4_id = create_epic(
        "Epic 4: Developer Experience (DevContainer)",
        "<p>Package the whole stack so any dev can spin it up in VS Code.</p>"
        "<p><strong>Phase:</strong> Phase 1 | <strong>Features:</strong> 1 | <strong>Stories:</strong> 3</p>"
        "<p><strong>Dependency:</strong> Requires Epic 3 (Agents & Skill) to be complete.</p>",
        priority=2, tags=["PoC", "Phase-1", "DevEx"], value_area="Architectural",
    )

    epic5_id = create_epic(
        "Epic 5: Additional Review Skills & Polish",
        "<p>Extend the pattern to Gender Tech and Budget review domains.</p>"
        "<p><strong>Phase:</strong> Phase 2 | <strong>Features:</strong> 4 | <strong>Stories:</strong> 5</p>"
        "<p><strong>Dependency:</strong> Requires Epic 3 (Agents & Skill) to be complete.</p>",
        priority=2, tags=["PoC", "Phase-2", "Skills"],
    )

    # ── Create Features ──
    print("\n── Creating Features ──")

    # Epic 0 Features
    f01_id = create_feature(
        "Feature 0.1: Define Target Folder Structure",
        "<p>Design the complete <code>poc/</code> directory layout covering all layers and document component-to-location mapping.</p>",
        parent_id=epic0_id, priority=1, tags=["PoC", "Phase-0", "Structure"], value_area="Architectural",
    )
    f02_id = create_feature(
        "Feature 0.2: Scaffold Directory Skeleton",
        "<p>Create the directory tree with <code>.gitkeep</code> files for all components under <code>poc/</code> and <code>.claude/</code>.</p>",
        parent_id=epic0_id, priority=1, tags=["PoC", "Phase-0", "Structure"], value_area="Architectural",
    )
    f03_id = create_feature(
        "Feature 0.3: Foundational Configuration Files",
        "<p>Create README, .env.example, update .gitignore, and finalise plan.md paths.</p>",
        parent_id=epic0_id, priority=1, tags=["PoC", "Phase-0", "Config"], value_area="Architectural",
    )

    # Epic 1 Features
    f11_id = create_feature(
        "Feature 1.1: Docker Compose Data Stores",
        "<p>Create <code>docker-compose.yml</code> with Neo4j 5.26, OpenSearch 2.17, and Azurite 3.33. Create <code>.env</code> with connection strings.</p>",
        parent_id=epic1_id, priority=1, tags=["PoC", "Phase-1", "Infrastructure", "Docker"],
    )
    f12_id = create_feature(
        "Feature 1.2: Neo4j Knowledge Graph Seeding",
        "<p>Create Cypher seed data with Documents, Themes, Indicators, Countries, FundingAreas and their relationships.</p>",
        parent_id=epic1_id, priority=1, tags=["PoC", "Phase-1", "Neo4j", "Seed"],
    )
    f13_id = create_feature(
        "Feature 1.3: OpenSearch Document Chunk Seeding",
        "<p>Create index mapping, seed 10-20 representative document chunks, and verify BM25 search works.</p>",
        parent_id=epic1_id, priority=1, tags=["PoC", "Phase-1", "OpenSearch", "Seed"],
    )

    # Epic 2 Features
    f21_id = create_feature(
        "Feature 2.1: Neo4j MCP Server Configuration",
        "<p>Add <code>neo4j</code> server to <code>.mcp.json</code> using <code>uvx mcp-neo4j-cypher</code> (stdio transport).</p>",
        parent_id=epic2_id, priority=1, tags=["PoC", "Phase-1", "MCP", "Neo4j"],
    )
    f22_id = create_feature(
        "Feature 2.2: Strategy Review MCP Server (Custom Python)",
        "<p>Build FastMCP Python server with <code>search_documents</code>, <code>search_chunks</code>, and <code>get_page_image</code> tools.</p>",
        parent_id=epic2_id, priority=1, tags=["PoC", "Phase-1", "MCP", "Python"],
    )

    # Epic 3 Features
    f31_id = create_feature(
        "Feature 3.1: Graph Traversal Sub-Agent",
        "<p>Create Neo4j Cypher specialist sub-agent using Sonnet model with access to Neo4j MCP tools.</p>",
        parent_id=epic3_id, priority=1, tags=["PoC", "Phase-1", "Agents", "Neo4j"],
    )
    f32_id = create_feature(
        "Feature 3.2: Document Search Sub-Agent",
        "<p>Create text search specialist sub-agent using Sonnet model with access to Strategy Review MCP tools.</p>",
        parent_id=epic3_id, priority=1, tags=["PoC", "Phase-1", "Agents", "OpenSearch"],
    )
    f33_id = create_feature(
        "Feature 3.3: Strategy Review Skill (End-to-End Orchestration)",
        "<p>Create the <code>/strategy-review</code> skill that classifies questions, dispatches to agents, and synthesises results with citations.</p>",
        parent_id=epic3_id, priority=1, tags=["PoC", "Phase-1", "Skills", "E2E"],
    )

    # Epic 4 Features
    f41_id = create_feature(
        "Feature 4.1: DevContainer Setup",
        "<p>Create <code>.devcontainer</code> config with Python 3.12, Node 22, port forwarding, linked to data tier.</p>",
        parent_id=epic4_id, priority=2, tags=["PoC", "Phase-1", "DevEx", "DevContainer"], value_area="Architectural",
    )

    # Epic 5 Features
    f51_id = create_feature(
        "Feature 5.1: Image Retrieval Sub-Agent",
        "<p>Create image retrieval sub-agent using <code>get_page_image</code> tool and seed Azurite with sample images.</p>",
        parent_id=epic5_id, priority=2, tags=["PoC", "Phase-2", "Agents"],
    )
    f52_id = create_feature(
        "Feature 5.2: Gender Tech Review Skill",
        "<p>Clone strategy-review skill focused on Theme <code>gender-equality</code>, Indicator <code>gdi</code>, FundingArea <code>gpe</code>.</p>",
        parent_id=epic5_id, priority=2, tags=["PoC", "Phase-2", "Skills"],
    )
    f53_id = create_feature(
        "Feature 5.3: Budget Review Skill",
        "<p>Clone strategy-review skill focused on FundingArea nodes, budget allocations, funding→theme relationships.</p>",
        parent_id=epic5_id, priority=2, tags=["PoC", "Phase-2", "Skills"],
    )
    f54_id = create_feature(
        "Feature 5.4: Unified Seed Script",
        "<p>Create <code>seed/seed-all.sh</code> — one command to seed all three data stores.</p>",
        parent_id=epic5_id, priority=2, tags=["PoC", "Phase-2", "Seed"],
    )

    # ── Create User Stories ──
    print("\n── Creating User Stories ──")

    # === Epic 0 Stories ===
    print("\n  [Epic 0: Project Structure & Scaffolding]")

    # Feature 0.1
    create_story(
        "Design complete poc/ directory layout",
        "Design the complete <code>poc/</code> directory layout covering all layers: infrastructure, seed data, MCP servers, and devcontainer.",
        "Documented structure covers every file/folder from the implementation plan.",
        parent_id=f01_id, priority=1, tags=["PoC", "Phase-0"],
    )
    create_story(
        "Document component-to-location mapping (poc/ vs repo root)",
        "Document which components live under <code>poc/</code> vs repo root (<code>.claude/</code> agents &amp; skills, <code>.mcp.json</code> must stay at root per Claude Code convention).",
        "Clear mapping of component → location with rationale.",
        parent_id=f01_id, priority=1, tags=["PoC", "Phase-0"],
    )

    # Feature 0.2
    create_story(
        "Create poc/seed/ directory tree with .gitkeep files",
        "Create the <code>poc/seed/neo4j/</code>, <code>poc/seed/opensearch/</code>, <code>poc/seed/azurite/</code> directory tree with <code>.gitkeep</code> files.",
        "All seed directories exist and are tracked by git.",
        parent_id=f02_id, priority=1, tags=["PoC", "Phase-0"],
    )
    create_story(
        "Create poc/mcp-servers/ directory tree with .gitkeep",
        "Create the <code>poc/mcp-servers/strategy-review/strategy_review_mcp/</code> directory tree with <code>.gitkeep</code>.",
        "MCP server package structure exists.",
        parent_id=f02_id, priority=1, tags=["PoC", "Phase-0"],
    )
    create_story(
        "Create .devcontainer/ directory at repo root",
        "Create the <code>.devcontainer/</code> directory at the repo root (required by VS Code).",
        "DevContainer directory exists at repo root.",
        parent_id=f02_id, priority=1, tags=["PoC", "Phase-0"],
    )
    create_story(
        "Create placeholder directories for agents and skills",
        "Create placeholder directories for future agents and skills under <code>.claude/</code>: <code>.claude/skills/strategy-review/</code>, <code>gender-tech-review/</code>, <code>budget-review/</code>.",
        "<code>.claude/agents/</code> and <code>.claude/skills/strategy-review/</code>, <code>gender-tech-review/</code>, <code>budget-review/</code> directories exist.",
        parent_id=f02_id, priority=1, tags=["PoC", "Phase-0"],
    )

    # Feature 0.3
    create_story(
        "Create poc/README.md with structure guide and layer descriptions",
        "Create <code>poc/README.md</code> documenting the project structure, layer descriptions, and component responsibilities.",
        "README explains each layer, how they connect, and which epic delivers each component.",
        parent_id=f03_id, priority=1, tags=["PoC", "Phase-0"],
    )
    create_story(
        "Create poc/.env.example with template connection strings",
        "Create <code>poc/.env.example</code> with template connection strings for Neo4j, OpenSearch, and Azurite.",
        "All required env vars listed with placeholder values and comments.",
        parent_id=f03_id, priority=1, tags=["PoC", "Phase-0"],
    )
    create_story(
        "Update .gitignore with poc/-specific patterns",
        "Update <code>.gitignore</code> with <code>poc/</code>-specific patterns (<code>.env</code>, data volumes, Python venvs, <code>__pycache__</code>).",
        "Sensitive files and build artefacts under <code>poc/</code> are excluded from git.",
        parent_id=f03_id, priority=1, tags=["PoC", "Phase-0"],
    )
    create_story(
        "Update plan.md with finalised poc/-scoped file paths",
        "Update <code>plan.md</code> with finalised file paths reflecting the <code>poc/</code>-scoped structure.",
        "All file paths in the plan match the agreed directory layout.",
        parent_id=f03_id, priority=1, tags=["PoC", "Phase-0"],
    )

    # === Epic 1 Stories ===
    print("\n  [Epic 1: Data Tier Infrastructure]")

    # Feature 1.1
    create_story(
        "Create docker-compose.yml with Neo4j, OpenSearch, and Azurite",
        "Create <code>docker-compose.yml</code> with Neo4j 5.26, OpenSearch 2.17, and Azurite 3.33.",
        "Ports 7474/7687, 9200, 10000 exposed and containers start successfully.",
        parent_id=f11_id, priority=1, tags=["PoC", "Phase-1", "Docker"],
    )
    create_story(
        "Create .env file with connection strings",
        "Create <code>.env</code> file with connection strings for all data stores (gitignored).",
        "File exists, not tracked by git.",
        parent_id=f11_id, priority=1, tags=["PoC", "Phase-1", "Config"],
    )
    create_story(
        "Verify all Docker containers start healthy",
        "Run <code>docker compose up -d &amp;&amp; docker compose ps</code> and verify all services are healthy.",
        "<code>docker compose ps</code> shows all containers as healthy.",
        parent_id=f11_id, priority=1, tags=["PoC", "Phase-1", "Verification"],
    )

    # Feature 1.2
    create_story(
        "Create seed/neo4j/seed.cypher with knowledge graph data",
        "Create <code>seed/neo4j/seed.cypher</code> with Documents, Themes, Indicators, Countries, FundingAreas and relationships.",
        "Cypher file creates nodes with COVERS_THEME, MEASURED_BY, PRIORITY_IN, ALLOCATES_TO, SUPPORTS_THEME relationships.",
        parent_id=f12_id, priority=1, tags=["PoC", "Phase-1", "Neo4j"],
    )
    create_story(
        "Create seed/neo4j/seed.sh runner script",
        "Create <code>seed/neo4j/seed.sh</code> that runs cypher-shell against the Neo4j container.",
        "Script executes cypher-shell against the Neo4j container successfully.",
        parent_id=f12_id, priority=1, tags=["PoC", "Phase-1", "Neo4j"],
    )
    create_story(
        "Verify knowledge graph in Neo4j browser",
        "Open Neo4j browser at <code>http://localhost:7474</code> and verify the graph.",
        "Neo4j browser shows the graph with all node types and relationships.",
        parent_id=f12_id, priority=1, tags=["PoC", "Phase-1", "Neo4j", "Verification"],
    )

    # Feature 1.3
    create_story(
        "Create seed/opensearch/create-index.sh with index mapping",
        "Create <code>seed/opensearch/create-index.sh</code> with index mapping for <code>strategy-chunks</code>.",
        "Index mapping created with appropriate fields.",
        parent_id=f13_id, priority=1, tags=["PoC", "Phase-1", "OpenSearch"],
    )
    create_story(
        "Create seed/opensearch/chunks.ndjson with document chunks",
        "Create <code>seed/opensearch/chunks.ndjson</code> with 10-20 representative document chunks.",
        "NDJSON file with realistic strategy document content.",
        parent_id=f13_id, priority=1, tags=["PoC", "Phase-1", "OpenSearch"],
    )
    create_story(
        "Create seed/opensearch/seed.sh for bulk indexing",
        "Create <code>seed/opensearch/seed.sh</code> that bulk-indexes chunks into OpenSearch.",
        "Script bulk-indexes chunks into OpenSearch successfully.",
        parent_id=f13_id, priority=1, tags=["PoC", "Phase-1", "OpenSearch"],
    )
    create_story(
        "Verify OpenSearch document search works",
        "Run <code>curl</code> query for 'maternal health' and verify it returns hits.",
        "<code>curl</code> query for 'maternal health' returns hits from the <code>strategy-chunks</code> index.",
        parent_id=f13_id, priority=1, tags=["PoC", "Phase-1", "OpenSearch", "Verification"],
    )

    # === Epic 2 Stories ===
    print("\n  [Epic 2: MCP Server Integration]")

    # Feature 2.1
    create_story(
        "Add neo4j server to .mcp.json",
        "Add <code>neo4j</code> server to <code>.mcp.json</code> using <code>uvx mcp-neo4j-cypher</code> (stdio transport).",
        "Config uses stdio transport, exposes <code>read_neo4j_cypher</code>, <code>write_neo4j_cypher</code>, <code>get_neo4j_schema</code>.",
        parent_id=f21_id, priority=1, tags=["PoC", "Phase-1", "MCP"],
    )
    create_story(
        "Verify Neo4j MCP tools visible in Claude Code",
        "Restart Claude Code, run <code>/mcp</code> and verify neo4j tools are visible. Ask Claude to get the DB schema.",
        "<code>/mcp</code> shows neo4j tools; Claude can get the DB schema.",
        parent_id=f21_id, priority=1, tags=["PoC", "Phase-1", "MCP", "Verification"],
    )

    # Feature 2.2
    create_story(
        "Create mcp-servers/strategy-review/pyproject.toml",
        "Create <code>mcp-servers/strategy-review/pyproject.toml</code> with deps: <code>mcp[cli]</code>, <code>opensearch-py</code>, <code>azure-storage-blob</code>.",
        "Project builds successfully with <code>uv</code>.",
        parent_id=f22_id, priority=1, tags=["PoC", "Phase-1", "MCP", "Python"],
    )
    create_story(
        "Implement search_documents(query, top_k) tool",
        "Implement <code>search_documents(query, top_k)</code> — BM25 search on OpenSearch.",
        "Returns ranked document results for a given query.",
        parent_id=f22_id, priority=1, tags=["PoC", "Phase-1", "MCP", "OpenSearch"],
    )
    create_story(
        "Implement search_chunks(query, doc_id, top_k) tool",
        "Implement <code>search_chunks(query, doc_id, top_k)</code> — granular chunk search.",
        "Returns chunk-level results filtered by <code>doc_id</code>.",
        parent_id=f22_id, priority=1, tags=["PoC", "Phase-1", "MCP", "OpenSearch"],
    )
    create_story(
        "Implement get_page_image(doc_id, page_num) tool",
        "Implement <code>get_page_image(doc_id, page_num)</code> — blob retrieval from Azurite (base64).",
        "Returns base64-encoded page image from Azurite.",
        parent_id=f22_id, priority=1, tags=["PoC", "Phase-1", "MCP", "Azurite"],
    )
    create_story(
        "Add strategy-review server to .mcp.json",
        "Add <code>strategy-review</code> server to <code>.mcp.json</code> using <code>uv run</code> (stdio transport).",
        "Server registered in MCP config.",
        parent_id=f22_id, priority=1, tags=["PoC", "Phase-1", "MCP"],
    )
    create_story(
        "Verify search_documents tool works end-to-end",
        "Restart Claude Code and test <code>search_documents</code> tool with a query.",
        "Claude can invoke tool and get search results.",
        parent_id=f22_id, priority=1, tags=["PoC", "Phase-1", "MCP", "Verification"],
    )

    # === Epic 3 Stories ===
    print("\n  [Epic 3: Sub-Agents & Strategy Review Skill]")

    # Feature 3.1
    create_story(
        "Create .claude/agents/graph-traversal.md agent definition",
        "Create <code>.claude/agents/graph-traversal.md</code> — Neo4j Cypher specialist (Sonnet model).",
        "Agent has access to <code>mcp__neo4j__read_neo4j_cypher</code> and <code>mcp__neo4j__get_neo4j_schema</code>.",
        parent_id=f31_id, priority=1, tags=["PoC", "Phase-1", "Agents"],
    )
    create_story(
        "Verify graph-traversal agent can query Neo4j",
        "Ask Claude to dispatch to the agent via Task tool and query the graph.",
        "Claude dispatches to agent and returns graph query results.",
        parent_id=f31_id, priority=1, tags=["PoC", "Phase-1", "Agents", "Verification"],
    )

    # Feature 3.2
    create_story(
        "Create .claude/agents/document-search.md agent definition",
        "Create <code>.claude/agents/document-search.md</code> — text search specialist (Sonnet model).",
        "Agent has access to <code>mcp__strategy_review__search_documents</code> and <code>search_chunks</code>.",
        parent_id=f32_id, priority=1, tags=["PoC", "Phase-1", "Agents"],
    )
    create_story(
        "Verify document-search agent can search and return documents",
        "Ask Claude to dispatch to the agent and search for documents.",
        "Claude dispatches to agent and returns search results.",
        parent_id=f32_id, priority=1, tags=["PoC", "Phase-1", "Agents", "Verification"],
    )

    # Feature 3.3
    create_story(
        "Create strategy-review SKILL.md with question classification",
        "Create <code>.claude/skills/strategy-review/SKILL.md</code> with question classification logic.",
        "Skill classifies questions as graph/text/combined.",
        parent_id=f33_id, priority=1, tags=["PoC", "Phase-1", "Skills"],
    )
    create_story(
        "Implement agent dispatch routing",
        "Implement agent dispatch — routes to graph-traversal and/or document-search based on question type.",
        "Correct agent(s) invoked based on question type.",
        parent_id=f33_id, priority=1, tags=["PoC", "Phase-1", "Skills"],
    )
    create_story(
        "Implement result synthesis with source citations",
        "Implement result synthesis that combines agent responses with source citations.",
        "Answer cites both graph and text sources.",
        parent_id=f33_id, priority=1, tags=["PoC", "Phase-1", "Skills"],
    )
    create_story(
        "End-to-end test: /strategy-review skill",
        "Run <code>/strategy-review What themes does the Global Health Strategy cover?</code> and verify full pipeline.",
        "Skill → Agent → MCP → Data Store → Synthesised answer with citations.",
        parent_id=f33_id, priority=1, tags=["PoC", "Phase-1", "E2E", "Verification"],
    )

    # === Epic 4 Stories ===
    print("\n  [Epic 4: Developer Experience (DevContainer)]")

    # Feature 4.1
    create_story(
        "Create .devcontainer/devcontainer.json",
        "Create <code>.devcontainer/devcontainer.json</code> with Python 3.12, Node 22, port forwarding.",
        "Config specifies correct base image and forwarded ports (7474, 7687, 9200, 10000).",
        parent_id=f41_id, priority=2, tags=["PoC", "Phase-1", "DevContainer"],
    )
    create_story(
        "Create .devcontainer/docker-compose.devcontainer.yml",
        "Create <code>.devcontainer/docker-compose.devcontainer.yml</code> linking workspace container to data tier.",
        "Workspace container can reach Neo4j, OpenSearch, Azurite.",
        parent_id=f41_id, priority=2, tags=["PoC", "Phase-1", "DevContainer"],
    )
    create_story(
        "Verify VS Code 'Reopen in Container' works",
        "Open VS Code, use 'Reopen in Container' and verify all services are up and MCP tools are available.",
        "All services up, MCP tools available inside container.",
        parent_id=f41_id, priority=2, tags=["PoC", "Phase-1", "DevContainer", "Verification"],
    )

    # === Epic 5 Stories ===
    print("\n  [Epic 5: Additional Review Skills & Polish]")

    # Feature 5.1
    create_story(
        "Create .claude/agents/image-retrieval.md agent",
        "Create <code>.claude/agents/image-retrieval.md</code> using <code>get_page_image</code> tool.",
        "Agent can retrieve and return page images.",
        parent_id=f51_id, priority=2, tags=["PoC", "Phase-2", "Agents"],
    )
    create_story(
        "Seed Azurite with sample page images",
        "Seed Azurite with sample page images in <code>seed/azurite/</code>.",
        "Images accessible via blob storage.",
        parent_id=f51_id, priority=2, tags=["PoC", "Phase-2", "Azurite", "Seed"],
    )

    # Feature 5.2
    create_story(
        "Create gender-tech-review SKILL.md",
        "Create <code>.claude/skills/gender-tech-review/SKILL.md</code> (cloned from strategy-review).",
        "Focuses on Theme <code>gender-equality</code>, Indicator <code>gdi</code>, FundingArea <code>gpe</code>.",
        parent_id=f52_id, priority=2, tags=["PoC", "Phase-2", "Skills"],
    )

    # Feature 5.3
    create_story(
        "Create budget-review SKILL.md",
        "Create <code>.claude/skills/budget-review/SKILL.md</code> (cloned from strategy-review).",
        "Focuses on FundingArea nodes, budget allocations, funding→theme relationships.",
        parent_id=f53_id, priority=2, tags=["PoC", "Phase-2", "Skills"],
    )

    # Feature 5.4
    create_story(
        "Create seed/seed-all.sh unified seed script",
        "Create <code>seed/seed-all.sh</code> — one command to seed all three stores (Neo4j, OpenSearch, Azurite).",
        "Single script seeds Neo4j, OpenSearch, and Azurite successfully.",
        parent_id=f54_id, priority=2, tags=["PoC", "Phase-2", "Seed"],
    )

    print("\n" + "=" * 60)
    print("Done! All work items created on Azure DevOps.")
    print("=" * 60)


if __name__ == "__main__":
    main()
