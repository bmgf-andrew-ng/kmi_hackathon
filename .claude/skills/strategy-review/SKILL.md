---
name: strategy-review
description: Search and analyse global health strategy documents using the knowledge graph and document corpus
argument-hint: Ask a question about global health strategies (e.g. "What funding is allocated to TB?")
---

# Strategy Review Skill

Answer questions about global health strategy documents by querying the Neo4j knowledge graph and OpenSearch document corpus.

## Workflow

### Step 1 — Receive the Question

The user provides their question via `$ARGUMENTS`.

If `$ARGUMENTS` is empty, ask the user what they'd like to know about the global health strategies. Suggest example questions:
- "How much funding is allocated to TB elimination?"
- "What does the Global Health Strategy say about malaria prevention?"
- "Which countries prioritise maternal health and what interventions are recommended?"

### Step 2 — Classify the Question

Before dispatching, classify the question into one of three categories:

**Graph** — use when the question asks about:
- Relationships between entities (documents, themes, countries, indicators, funding areas)
- Funding amounts, budget allocations, or percentages
- Country priorities, rankings, or implementation progress
- Indicator baselines, targets, or measurements
- Comparisons across entities (e.g. "which theme gets the most funding?")

**Text** — use when the question asks about:
- Specific policy details, recommendations, or interventions
- Quotes or passages from strategy documents
- Section content or document summaries
- Contextual explanations or rationale behind strategies

**Both** — use when:
- The question needs structural data AND textual evidence
- The question is complex or multi-part
- The category is ambiguous — when in doubt, use Both

Classification examples:
- "How much funding is allocated to TB?" → **Graph**
- "What are the TB treatment success rate targets?" → **Graph**
- "Which countries support HIV programmes?" → **Graph**
- "What does the GH Strategy say about malaria prevention?" → **Text**
- "Summarise the TB Elimination Plan's approach to drug-resistant TB" → **Text**
- "What gender-responsive budgeting recommendations exist?" → **Text**
- "Which countries prioritise maternal health and what interventions are recommended?" → **Both**
- "What is the funding for digital health and how will it be spent?" → **Both**
- "Compare TB approaches across the Global Health Strategy and TB Elimination Plan" → **Both**

### Step 3 — Dispatch to Sub-Agents

Based on the classification, dispatch using the Task tool.

#### If Graph:

Launch a single Task with `subagent_type: "general-purpose"` and the following prompt:

```
You are a Neo4j Cypher specialist querying a global health strategy knowledge graph.

Use the `mcp__neo4j__read_neo4j_cypher` tool to answer this question:

${ARGUMENTS}

## Graph Schema

Node types:
- Document: id, title, type, year, organization, region
- Theme: id, name, description, priority
- Indicator: id, name, unit, target
- Country: code, name, region, income_level
- FundingArea: id, name, budget_usd_millions, fiscal_year

Relationships:
- (Document)-[:COVERS_THEME {primary, weight}]->(Theme)
- (Theme)-[:MEASURED_BY {baseline, target, year}]->(Indicator)
- (Theme)-[:PRIORITY_IN {rank, rationale}]->(Country)
- (FundingArea)-[:ALLOCATES_TO {amount_usd_millions, percentage}]->(Theme)
- (Country)-[:SUPPORTS_THEME {implementation_status, progress_pct}]->(Theme)

Guidelines:
- Use parameterised queries where possible
- Always include LIMIT clauses
- Return specific properties, not full nodes
- Present results as structured data with context
```

#### If Text:

Launch a single Task with `subagent_type: "general-purpose"` and the following prompt:

```
You are a text search specialist querying a global health strategy document corpus.

Use the Strategy Review MCP tools to answer this question:

${ARGUMENTS}

## Available Tools

1. `mcp__strategy-review__search_documents(query, top_k=5)` — broad document-level search
2. `mcp__strategy-review__search_chunks(query, doc_id=None, top_k=5)` — granular chunk search, optionally filtered by doc_id
3. `mcp__strategy-review__get_page_image(doc_id, page_num)` — retrieve original page image

## Document Corpus

- GH_2024: Global Health Strategy 2024-2028 (Global Fund)
- TB_2025: TB Elimination Plan 2025-2030 (WHO)
- GE_2023: Gender & Health Equity Framework 2023-2028 (Global Fund)

## Search Strategy

1. Start broad with search_documents to find relevant documents
2. Drill down with search_chunks filtered by doc_id for specific passages
3. Always cite: document title, section name, and page number

Present results as structured summaries with exact quotes where relevant.
```

#### If Both:

Launch TWO Task calls in parallel (both with `subagent_type: "general-purpose"`), one with the Graph prompt and one with the Text prompt above. Wait for both to return before proceeding to synthesis.

### Step 4 — Synthesise Results with Citations

Once the agent(s) return, synthesise the results into a single coherent response.

#### Output Format

```
## Answer

[Concise 2-3 sentence summary directly answering the question]

## Evidence

[Detailed supporting information organised by sub-topic. Every claim must have an inline citation.]

For graph-sourced data, cite as: *(Knowledge Graph: Node→Relationship→Node)*
For text-sourced data, cite as: *(Document Title, Section Name, p.XX)*

## Sources

[Numbered reference list]
1. [Document or data source with specific section/query referenced]
2. ...
```

#### Synthesis Guidelines

- Lead with the direct answer — don't bury it in evidence
- When both agents return data, weave graph and text results together rather than presenting them in separate blocks
- If graph data and text data conflict, flag the discrepancy and present both
- Use tables for comparative data (funding amounts, country rankings, indicator targets)
- Quote document text exactly when it adds value — use block quotes with citation

### Step 5 — Offer Follow-Up Questions

After presenting the synthesised answer, suggest 2-3 related questions the user might want to explore next. Base these on:
- Adjacent themes or countries mentioned in the results
- Deeper dives into data points surfaced
- Cross-cutting questions that span both graph and text

Format as:
```
**Want to dig deeper?**
- [Related question 1]
- [Related question 2]
- [Related question 3]
```

## Example Usage

```
/strategy-review What funding is allocated to maternal and newborn health?
```

Expected classification: **Graph** (funding allocation query)
Expected dispatch: graph-traversal agent queries FundingArea→ALLOCATES_TO→Theme
Expected output: table of funding areas with amounts, total sum, with citations to graph structure

```
/strategy-review What does the Gender & Health Equity Framework recommend for reducing maternal mortality?
```

Expected classification: **Text** (policy recommendation query)
Expected dispatch: document-search agent searches GE_2023 chunks
Expected output: summary of recommendations with quotes, section and page citations

```
/strategy-review Which countries prioritise TB elimination and what interventions are planned?
```

Expected classification: **Both** (country priorities from graph + intervention details from text)
Expected dispatch: both agents in parallel
Expected output: country priority rankings from graph woven with intervention details from text
