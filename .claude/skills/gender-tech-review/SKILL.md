---
name: gender-tech-review
description: Analyse gender equality, women's health, and health equity aspects of global health strategies
argument-hint: Ask a question about gender and health equity (e.g. "What is the GDI target for 2028?")
---

# Gender & Tech Review Skill

Answer questions about gender equality, women's health, and health equity in global health strategy documents by querying the Neo4j knowledge graph and OpenSearch document corpus.

This skill focuses on the **Gender Equality & Women's Health** theme, the **Gender & Health Equity Framework (GE_2023)**, related indicators (GDI, MMR, NMR), and the GPE funding area.

## Workflow

### Step 1 — Receive the Question

The user provides their question via `$ARGUMENTS`.

If `$ARGUMENTS` is empty, ask the user what they'd like to know about gender and health equity. Suggest example questions:
- "What does the Gender & Health Equity Framework recommend for reducing maternal mortality?"
- "What is the Gender Development Index target and current baseline?"
- "How much funding is allocated to gender and health equity?"
- "Which countries prioritise maternal and newborn health?"

### Step 2 — Classify the Question

Before dispatching, classify the question into one of three categories:

**Graph** — use when the question asks about:
- Gender Development Index (GDI) baselines, targets, or progress
- Maternal mortality or neonatal mortality indicators (MMR, NMR)
- GPE funding area allocations and percentages
- Country priorities for maternal & newborn health or gender equality
- Relationships between the GENDER or MNH themes and other entities

**Text** — use when the question asks about:
- Gender-responsive budgeting recommendations
- Women's health access barriers or interventions
- Policy details from the Gender & Health Equity Framework (GE_2023)
- Specific passages about gender mainstreaming or equity approaches
- Contextual explanations of gender-related health strategies

**Both** — use when:
- The question needs structural data AND textual evidence
- The question is complex or multi-part
- The category is ambiguous — when in doubt, use Both

Classification examples:
- "What is the GDI target for 2028?" -> **Graph**
- "How much funding goes to gender and health equity?" -> **Graph**
- "Which countries prioritise maternal health?" -> **Graph**
- "What does the GE Framework say about gender-responsive budgeting?" -> **Text**
- "What barriers to women's health access are identified?" -> **Text**
- "What is the maternal mortality target and what interventions are recommended to achieve it?" -> **Both**
- "How is the GPE funding allocated and what programmes does it support?" -> **Both**

### Step 3 — Dispatch to Sub-Agents

Based on the classification, dispatch using the Task tool.

#### If Graph:

Launch a single Task with `subagent_type: "general-purpose"` and the following prompt:

```
You are a Neo4j Cypher specialist querying a global health strategy knowledge graph. Focus on gender equality, women's health, and health equity data.

Use the `mcp__neo4j__read_neo4j_cypher` tool to answer this question:

${ARGUMENTS}

## Graph Schema

Node types:
- Document: id, title, type, year, organization, region
- Theme: id, name, description, priority — focus on GENDER ('Gender Equality & Womens Health') and MNH ('Maternal & Newborn Health')
- Indicator: id, name, unit, target — focus on GDI ('Gender Development Index'), MMR ('Maternal Mortality Ratio'), NMR ('Neonatal Mortality Rate'), FACILITY ('Health Facility Density')
- Country: code, name, region, income_level
- FundingArea: id, name, budget_usd_millions, fiscal_year — focus on GPE ('Gender & Health Equity', $50M)

Relationships:
- (Document)-[:COVERS_THEME {primary, weight}]->(Theme)
- (Theme)-[:MEASURED_BY {baseline, target, year}]->(Indicator)
- (Theme)-[:PRIORITY_IN {rank, rationale}]->(Country)
- (FundingArea)-[:ALLOCATES_TO {amount_usd_millions, percentage}]->(Theme)
- (Country)-[:SUPPORTS_THEME {implementation_status, progress_pct}]->(Theme)

Key data points:
- GE_2023 covers GENDER (weight 95) and MNH (weight 80)
- GH_2024 also covers GENDER (weight 75) and MNH (weight 95)
- GPE allocates $30M (60%) to GENDER and $20M (40%) to MNH
- GDI baseline: 0.82, target: 1.0 by 2028
- MMR baseline: 223, target: 70 per 100k live births by 2028

Guidelines:
- Use parameterised queries where possible
- Always include LIMIT clauses
- Return specific properties, not full nodes
- Present results as structured data with context
```

#### If Text:

Launch a single Task with `subagent_type: "general-purpose"` and the following prompt:

```
You are a text search specialist querying a global health strategy document corpus. Focus on gender equality, women's health, and health equity content.

Use the Strategy Review MCP tools to answer this question:

${ARGUMENTS}

## Available Tools

1. `mcp__strategy-review__search_documents(query, top_k=5)` — broad document-level search
2. `mcp__strategy-review__search_chunks(query, doc_id=None, top_k=5)` — granular chunk search, optionally filtered by doc_id
3. `mcp__strategy-review__get_page_image(doc_id, page_num)` — retrieve original page image

## Document Corpus (gender-relevant)

- GE_2023: Gender & Health Equity Framework 2023-2028 (Global Fund) — PRIMARY source for gender content
- GH_2024: Global Health Strategy 2024-2028 (Global Fund) — secondary source for gender-related sections
- TB_2025: TB Elimination Plan 2025-2030 (WHO) — may contain gender-disaggregated TB data

## Search Strategy

1. Start with search_chunks filtered by doc_id='GE_2023' for gender-specific content
2. Broaden with search_documents if GE_2023 doesn't have enough coverage
3. Search GH_2024 for complementary gender-related strategy content
4. Always cite: document title, section name, and page number

Present results as structured summaries with exact quotes where relevant.
```

#### If Both:

Launch TWO Task calls in parallel (both with `subagent_type: "general-purpose"`), one with the Graph prompt and one with the Text prompt above. Wait for both to return before proceeding to synthesis.

### Step 4 — Synthesise Results with Citations

Once the agent(s) return, synthesise the results into a single coherent response with a gender and health equity lens.

#### Output Format

```
## Answer

[Concise 2-3 sentence summary directly answering the question through a gender/equity lens]

## Evidence

[Detailed supporting information organised by sub-topic. Every claim must have an inline citation.]

For graph-sourced data, cite as: *(Knowledge Graph: Node->Relationship->Node)*
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
- Use tables for comparative data (GDI scores, maternal mortality rates, funding allocations)
- Quote document text exactly when it adds value — use block quotes with citation
- Highlight gender-specific findings and cross-cutting equity implications

### Step 5 — Offer Follow-Up Questions

After presenting the synthesised answer, suggest 2-3 related questions the user might want to explore next. Base these on gender and health equity themes:

Format as:
```
**Want to dig deeper?**
- [Related question 1]
- [Related question 2]
- [Related question 3]
```

## Example Usage

```
/gender-tech-review What is the Gender Development Index target and how is progress tracked?
```

Expected classification: **Graph** (indicator query)
Expected dispatch: graph-traversal queries Theme(GENDER)-[:MEASURED_BY]->Indicator(GDI)
Expected output: GDI baseline 0.82, target 1.0 by 2028, with context from the GENDER theme

```
/gender-tech-review What does the Gender & Health Equity Framework recommend for reducing maternal mortality?
```

Expected classification: **Text** (policy recommendation query)
Expected dispatch: document-search searches GE_2023 chunks for maternal mortality recommendations
Expected output: summary of recommendations with quotes, section and page citations

```
/gender-tech-review How is gender equity funding allocated and what programmes does it support?
```

Expected classification: **Both** (funding data from graph + programme details from text)
Expected dispatch: both agents in parallel
Expected output: GPE allocation table from graph woven with programme descriptions from text
