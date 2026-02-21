from __future__ import annotations

import json
import re
import tempfile
import time

import requests
from ibm_watsonx_orchestrate.agent_builder.tools import ToolPermission, tool


WO_INSTANCE = ""
WO_API_KEY = ""
KB_NAME = "incident_runbooks_kb"


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "new-incident"


def _headers() -> dict:
    token_resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": WO_API_KEY,
        },
        timeout=20,
    )
    token_resp.raise_for_status()
    access_token = token_resp.json().get("access_token")
    if not access_token:
        raise RuntimeError("missing access_token from IAM response")
    return {"Authorization": f"Bearer {access_token}"}


def _sync_entry_to_kb(filename: str, text_entry: str) -> str:
    list_url = f"{WO_INSTANCE}/v1/orchestrate/knowledge-bases"
    list_resp = requests.get(list_url, headers=_headers(), params={"names": KB_NAME}, timeout=20)
    list_resp.raise_for_status()
    kbs = list_resp.json()
    if not kbs:
        return f"kb_sync_failed: knowledge base '{KB_NAME}' not found"

    kb_id = kbs[0].get("id")
    if not kb_id:
        return "kb_sync_failed: missing knowledge base id"

    status_url = f"{WO_INSTANCE}/v1/orchestrate/knowledge-bases/{kb_id}/status"
    status_before = requests.get(status_url, headers=_headers(), timeout=20)
    status_before.raise_for_status()
    docs_before = len(status_before.json().get("documents", []))

    ingest_url = f"{WO_INSTANCE}/v1/orchestrate/knowledge-bases/{kb_id}/documents"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=True) as tmp:
        tmp.write(text_entry)
        tmp.flush()
        with open(tmp.name, "rb") as file_handle:
            files = {"files": (filename, file_handle, "text/plain")}
            data = {"file_urls": json.dumps({})}
            ingest_resp = requests.put(ingest_url, headers=_headers(), data=data, files=files, timeout=30)
            ingest_resp.raise_for_status()

    status_after = requests.get(status_url, headers=_headers(), timeout=20)
    status_after.raise_for_status()
    docs_after = len(status_after.json().get("documents", []))
    if docs_after < docs_before:
        return f"kb_sync_failed: document count decreased ({docs_before} -> {docs_after})"
    return f"kb_sync_ok: documents {docs_before} -> {docs_after}"


@tool(permission=ToolPermission.READ_WRITE)
def draft_runbook_entry(
    title: str,
    service: str,
    environment: str,
    symptoms: str,
    likely_causes: str,
    immediate_mitigation: str,
    escalation_triggers: str,
    verification_steps: str,
) -> str:
    """
    Generate a plain-text runbook entry and auto-sync it to the knowledge base.
    """
    slug = _slugify(title)
    filename = f"custom-{slug}-{int(time.time())}.txt"
    text_entry = f"""=== RUNBOOK ENTRY START ===
Title: {title.strip()}
Slug: {slug}
Service: {service.strip()}
Environment: {environment.strip()}

Symptoms:
{symptoms.strip()}

Likely Causes:
{likely_causes.strip()}

Immediate Mitigation:
{immediate_mitigation.strip()}

Escalation:
{escalation_triggers.strip()}

Verification:
{verification_steps.strip()}
=== RUNBOOK ENTRY END ===
"""

    try:
        sync_status = _sync_entry_to_kb(filename, text_entry)
    except Exception as exc:
        return (
            f"runbook_generated_but_sync_failed: {exc}\n"
            f"filename: {filename}\n"
            "retry upload by re-running this action"
        )

    return (
        f"runbook_synced: {sync_status}\n"
        f"filename: {filename}\n"
        "entry uploaded to incident_runbooks_kb"
    )
