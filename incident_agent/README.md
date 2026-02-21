# Enterprise Incident Knowledge Agent (KB-First Edition)

A lightweight incident assistant that collects incident details via chat form, searches runbooks in a managed knowledge base, and provides concise triage insights.

## Setup

1) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r incident_agent/requirements.txt
```

3) Configure ticket settings

The current tool implementations use values hardcoded in:
- `incident_agent/agent_spec/tools/create_incident_ticket.py`

```bash
GITHUB_REPO, GITHUB_TOKEN
```

## KB-first architecture

```
User question -> Orchestrate Agent (react) -> incident_runbooks_kb -> grounded answer + insights
```

Runbooks live in: `incident_agent/kb/runbooks`

## Chat intake form behavior

The agent asks for:
- Service
- Environment
- Symptoms/Error
- Time window
- User impact
- Recent changes (deploy/config/infrastructure)

It then builds a focused search query and returns plain-language guidance (not JSON), including summary, checks, mitigations, escalation triggers, confidence, and cited runbook filenames.

## Add new incident knowledge

The agent can guide a runbook submission workflow in chat:
- It collects a structured runbook form (title, symptoms, causes, mitigation, escalation, verification).
- It generates a text runbook entry and attempts automatic KB sync via `draft_runbook_entry`.
- It uses helper tools:
  - `build_incident_search_query`
  - `draft_runbook_entry`
  - `create_incident_ticket`

If auto-sync fails, the tool returns fallback instructions to append to
`incident_agent/kb/runbooks_txt/custom-incidents.txt` and run KB import manually.

## Orchestrate specs

- Knowledge base spec: `incident_agent/agent_spec/incident_runbooks_kb.yaml`
- Agent spec: `incident_agent/agent_spec/incident_triage_agent.yaml`

Import into your active environment:

```bash
orchestrate tools import -k python -f incident_agent/agent_spec/tools/build_incident_search_query.py
orchestrate tools import -k python -f incident_agent/agent_spec/tools/draft_runbook_entry.py
orchestrate tools import -k python -f incident_agent/agent_spec/tools/create_incident_ticket.py
orchestrate knowledge-bases import -f incident_agent/agent_spec/incident_runbooks_kb.yaml
orchestrate agents import -f incident_agent/agent_spec/incident_triage_agent.yaml
```


`Title: Payment API timeout spike after DB config change
Service: payment-api
Environment: prod
Symptoms / Error description: Starting at 14:05 UTC, payment-api p95 latency increased from 220ms to 2.8s with frequent database timeout errors. Checkout failures rose to 11% and retry volume doubled.
Likely causes: Recent DB connection pool limit was reduced too aggressively; read replica lag increased under peak load; one app pod has stale DB DNS/cache causing intermittent connection routing issues.
Immediate mitigation / Fix steps: 1) Revert DB pool settings to previous known-good values. 2) Restart payment-api pods in rolling fashion to clear stale connections. 3) Temporarily scale payment-api from 6 to 10 replicas. 4) Enable circuit breaker fallback for non-critical payment enrichment calls. 5) Increase DB timeout threshold from 2s to 5s as a temporary stabilization measure.
Escalation triggers / contacts: Escalate to DB on-call immediately if error rate stays >5% for 10 minutes after mitigation. Escalate to incident commander if checkout conversion drops >8% for 15 minutes. Contacts: DB On-call (pager rotation), Payments Eng Lead, Incident Commander.
Verification steps (how to confirm the issue is resolved): Confirm payment-api timeout errors <0.5% for 20 minutes, p95 latency <400ms, checkout success rate back to baseline (+/-2%), no replica lag alerts, and no new customer complaint spikes in support channel.`