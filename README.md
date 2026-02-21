# Incident Triage Agent

A simple AI agent for incident response.
It collects incident details, searches runbooks in a knowledge base (RAG), and returns actionable triage guidance.

## What This Agent Is Meant To Do

- Help responders quickly triage production incidents.
- Ask for key details using a lightweight intake flow.
- Search runbooks and return grounded steps.
- Suggest checks, mitigation, escalation triggers, and confidence.
- Optionally create a ticket when explicitly requested.
- Optionally add new runbook knowledge into the KB.

## Core Features

- Guided incident intake
  - Starts with: `Service`, `Environment`, `Symptoms/Error`
  - Asks for more context only when needed: `Time window`, `User impact`, `Recent changes`
- KB-first runbook search
  - Uses `incident_runbooks_kb` as the source of truth
  - Returns concise, plain-language answers (not JSON)
- Structured response output
  - `Summary`
  - `First checks`
  - `Immediate mitigation`
  - `Escalation triggers`
  - `Confidence`
  - `Sources`
- New runbook submission workflow
  - Collects required fields
  - Generates a runbook entry
  - Attempts KB sync automatically
- Optional operational actions
  - `create_incident_ticket` (GitHub issue)
  - `send_incident_email` utility is included in repo tools

## Repository Layout

- Agent spec: `incident_agent/agent_spec/incident_triage_agent.yaml`
- Knowledge base spec: `incident_agent/agent_spec/incident_runbooks_kb.yaml`
- Tool code: `incident_agent/agent_spec/tools/`
- Runbook source document: `incident_agent/kb/runbooks_txt/all_runbook.txt`
- Dependencies: `incident_agent/requirements.txt`

## How It Works (Simple Flow)

1. User reports an incident.
2. Agent gathers minimum details.
3. Agent builds a focused search query (`build_incident_search_query`).
4. Agent retrieves relevant runbook content from `incident_runbooks_kb` (RAG retrieval).
5. Agent responds with practical triage steps.
6. If asked, agent creates a ticket (`create_incident_ticket`).
7. If asked, agent drafts and syncs a new runbook (`draft_runbook_entry`).

## Quick Start

1. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r incident_agent/requirements.txt
```

3. Import tools, KB, and agent.

```bash
orchestrate tools import -k python -f incident_agent/agent_spec/tools/build_incident_search_query.py
orchestrate tools import -k python -f incident_agent/agent_spec/tools/draft_runbook_entry.py
orchestrate tools import -k python -f incident_agent/agent_spec/tools/create_incident_ticket.py
orchestrate knowledge-bases import -f incident_agent/agent_spec/incident_runbooks_kb.yaml
orchestrate agents import -f incident_agent/agent_spec/incident_triage_agent.yaml
```

## Configuration Notes

- `create_incident_ticket` currently needs GitHub repo/token values configured in `incident_agent/agent_spec/tools/create_incident_ticket.py`.
- `draft_runbook_entry` needs Watsonx Orchestrate instance/API key values in `incident_agent/agent_spec/tools/draft_runbook_entry.py`.
- `send_incident_email` has SMTP placeholders in `incident_agent/agent_spec/tools/send_incident_email.py` and is optional.

## Example Prompt

`Help me triage an incident. Service: payment-api. Environment: prod. Symptoms/Error: DB timeout spikes after a config change.`
