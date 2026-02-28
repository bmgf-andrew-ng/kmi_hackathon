---
name: budget-review
description: Analyse funding allocations, budget breakdowns, and financial planning across global health strategies
argument-hint: Ask a question about funding and budgets (e.g. "How is disease prevention funding allocated?")
---

# Budget Review Skill

Answer questions about funding allocations, budget breakdowns, and financial planning in global health strategy documents by querying the Neo4j knowledge graph and OpenSearch document corpus.

This skill focuses on **FundingArea** nodes (HSS, PREV, GPE, DIGI, CAPACITY), their **ALLOCATES_TO** relationships with themes, and budget-related content across all strategy documents.

## Workflow

### Step 1 — Receive the Question

The user provides their question via `$ARGUMENTS`.

If `$ARGUMENTS` is empty, ask the user what they'd like to know about funding and budgets. Suggest example questions:
- "How is disease prevention funding allocated across themes?"
- "What is the total budget for health systems strengthening?"
- "Compare funding allocations across all funding areas"
- "What percentage of funding goes to TB elimination?"

### Step 2 — Classify the Question

Before dispatching, classify the question into one of three categories:

**Graph** — use when the question asks about:
- Specific funding amounts or budget totals
- Allocation percentages across themes
- Comparisons between funding areas
- Which themes receive the most/least funding
- FundingArea properties (budget_usd_millions, fiscal_year)
- Aggregated financial data (totals, averages, rankings)

**Text** — use when the question asks about:
- Budget justifications or rationale behind allocations
- Spending guidelines or financial governance
- Implementation cost details or programme budgets
- Funding sustainability or future financial planning
- Policy language around resource allocation

**Both** — use when:
- The question needs financial data AND contextual explanation
- The question is complex or multi-part
- The category is ambiguous — when in doubt, use Both

Classification examples:
- "How much funding goes to disease prevention?" -> **Graph**
- "What is the total budget across all funding areas?" -> **Graph**
- "Which theme gets the most funding?" -> **Graph**
- "Compare HSS and PREV allocations" -> **Graph**
- "What is the rationale behind digital health investment?" -> **Text**
- "What spending guidelines exist for gender equity programmes?" -> **Text**
- "How is TB elimination funded and what programmes does the budget support?" -> **Both**
- "What is the digital health budget and how will it be spent?" -> **Both**

**Note:** Most budget/funding questions will classify as **Graph** since financial data is structured in Neo4j. Use Text or Both when the question asks "why" or "how" beyond the numbers.

### Step 3 — Dispatch to Sub-Agents

Based on the classification, dispatch using the Task tool.

#### If Graph:

Launch a single Task with `subagent_type: "general-purpose"` and the following prompt:

```
You are a Neo4j Cypher specialist querying a global health strategy knowledge graph. Focus on funding allocations, budget analysis, and financial data.

Use the `mcp__neo4j__read_neo4j_cypher` tool to answer this question:

${ARGUMENTS}

## Graph Schema

Node types:
- FundingArea: id, name, budget_usd_millions, fiscal_year
- Theme: id, name, description, priority
- Document: id, title, type, year, organization, region
- Country: code, name, region, income_level
- Indicator: id, name, unit, target

Key relationship for budget queries:
- (FundingArea)-[:ALLOCATES_TO {amount_usd_millions, percentage}]->(Theme)

Supporting relationships:
- (Document)-[:COVERS_THEME {primary, weight}]->(Theme)
- (Theme)-[:MEASURED_BY {baseline, target, year}]->(Indicator)
- (Theme)-[:PRIORITY_IN {rank, rationale}]->(Country)
- (Country)-[:SUPPORTS_THEME {implementation_status, progress_pct}]->(Theme)

## Funding Areas (FY2024)

| ID | Name | Budget ($M) |
|----|------|-------------|
| HSS | Health Systems Strengthening | 150 |
| PREV | Disease Prevention Programs | 200 |
| GPE | Gender & Health Equity | 50 |
| DIGI | Digital Innovation & Data | 75 |
| CAPACITY | Capacity Building & Training | 60 |
| **Total** | | **535** |

## Useful Query Patterns

- Total budget: `MATCH (f:FundingArea) RETURN sum(f.budget_usd_millions)`
- Allocations by theme: `MATCH (f:FundingArea)-[a:ALLOCATES_TO]->(t:Theme) RETURN t.name, sum(a.amount_usd_millions) ORDER BY sum(a.amount_usd_millions) DESC`
- Funding for a specific theme: `MATCH (f:FundingArea)-[a:ALLOCATES_TO]->(t:Theme {id: 'TB'}) RETURN f.name, a.amount_usd_millions, a.percentage`

Guidelines:
- Use parameterised queries where possible
- Always include LIMIT clauses
- Return specific properties, not full nodes
- Present financial data in tables with totals
- Include percentages alongside absolute amounts
```

#### If Text:

Launch a single Task with `subagent_type: "general-purpose"` and the following prompt:

```
You are a text search specialist querying a global health strategy document corpus. Focus on funding rationale, budget justifications, and financial planning content.

Use the Strategy Review MCP tools to answer this question:

${ARGUMENTS}

## Available Tools

1. `mcp__strategy-review__search_documents(query, top_k=5)` — broad document-level search
2. `mcp__strategy-review__search_chunks(query, doc_id=None, top_k=5)` — granular chunk search, optionally filtered by doc_id
3. `mcp__strategy-review__get_page_image(doc_id, page_num)` — retrieve original page image

## Document Corpus

- GH_2024: Global Health Strategy 2024-2028 (Global Fund) — likely contains overall budget framework and allocation strategy
- TB_2025: TB Elimination Plan 2025-2030 (WHO) — may contain TB-specific costing and funding needs
- GE_2023: Gender & Health Equity Framework 2023-2028 (Global Fund) — contains gender equity funding rationale

## Search Strategy

1. Search for budget/funding/allocation-related terms across all documents
2. Drill down with search_chunks filtered by doc_id for specific financial sections
3. Look for terms like: "budget", "funding", "allocation", "investment", "resource", "cost", "financial"
4. Always cite: document title, section name, and page number

Present results as structured summaries with exact quotes where relevant.
```

#### If Both:

Launch TWO Task calls in parallel (both with `subagent_type: "general-purpose"`), one with the Graph prompt and one with the Text prompt above. Wait for both to return before proceeding to synthesis.

### Step 4 — Synthesise Results with Citations

Once the agent(s) return, synthesise the results into a single coherent response focused on financial analysis.

#### Output Format

```
## Answer

[Concise 2-3 sentence summary directly answering the budget/funding question]

## Financial Summary

[Present key financial data in a table where applicable]

| Funding Area | Budget ($M) | Allocation | Theme |
|---|---|---|---|
| ... | ... | ... | ... |

## Evidence

[Detailed supporting information organised by sub-topic. Every claim must have an inline citation.]

For graph-sourced data, cite as: *(Knowledge Graph: FundingArea->ALLOCATES_TO->Theme)*
For text-sourced data, cite as: *(Document Title, Section Name, p.XX)*

## Sources

[Numbered reference list]
1. [Document or data source with specific section/query referenced]
2. ...
```

#### Synthesis Guidelines

- Lead with the direct answer — don't bury it in evidence
- Always present financial data in tables with totals and percentages
- When both agents return data, weave graph and text results together rather than presenting them in separate blocks
- If graph data and text data conflict, flag the discrepancy and present both
- Round dollar amounts consistently (millions with 1 decimal)
- Include both absolute amounts and percentages for allocations
- Highlight notable patterns (largest/smallest allocations, funding gaps)

### Step 5 — Offer Follow-Up Questions

After presenting the synthesised answer, suggest 2-3 related questions the user might want to explore next. Base these on financial and budget themes:

Format as:
```
**Want to dig deeper?**
- [Related question 1]
- [Related question 2]
- [Related question 3]
```

## Example Usage

```
/budget-review How is disease prevention funding allocated across themes?
```

Expected classification: **Graph** (funding allocation query)
Expected dispatch: graph-traversal queries FundingArea(PREV)-[:ALLOCATES_TO]->Theme
Expected output: table showing PREV allocates $90M (45%) to Malaria, $60M (30%) to TB, $50M (25%) to Vaccines

```
/budget-review What is the rationale behind the digital health investment?
```

Expected classification: **Text** (budget justification query)
Expected dispatch: document-search searches for digital health funding rationale
Expected output: summary of strategy text explaining the $75M DIGI investment with quotes and citations

```
/budget-review What is the total budget and how is it distributed across all themes?
```

Expected classification: **Both** (aggregate data from graph + context from text)
Expected dispatch: both agents in parallel
Expected output: comprehensive budget table from graph with contextual justification from text
