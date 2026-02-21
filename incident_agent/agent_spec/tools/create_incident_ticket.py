from __future__ import annotations

import json
from urllib import request, error

from ibm_watsonx_orchestrate.agent_builder.tools import ToolPermission, tool


@tool(permission=ToolPermission.READ_WRITE)
def create_incident_ticket(
    service: str,
    environment: str,
    severity: str,
    summary: str,
    recommended_actions: str,
) -> str:
    """
    Create an incident ticket as a GitHub issue.

    Required runtime env vars:
      - GITHUB_REPO: owner/repo (example: octocat/Hello-World)
      - GITHUB_TOKEN: GitHub token with issues:write permission
    """
    
    github_repo = ""
    github_token = ""
    if not github_repo:
        return "ticket_skipped: missing GITHUB_REPO runtime secret"
    if not github_token:
        return "ticket_skipped: missing GITHUB_TOKEN runtime secret"

    issue_title = f"[{severity}] {service} incident in {environment}: {summary}"
    issue_body = (
        f"## Incident Details\n"
        f"- Service: {service}\n"
        f"- Environment: {environment}\n"
        f"- Severity: {severity}\n"
        f"- Summary: {summary}\n\n"
        f"## Recommended Actions\n{recommended_actions}\n"
    )

    payload = {"title": issue_title, "body": issue_body, "labels": ["incident", severity.lower()]}

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "incident-triage-agent",
    }

    issues_url = f"https://api.github.com/repos/{github_repo}/issues"
    req = request.Request(
        issues_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=15) as response:
            body = response.read().decode("utf-8") if response else ""
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        return f"ticket_failed: http_{exc.code} {details}".strip()
    except Exception as exc:
        return f"ticket_failed: {exc}"

    if not body:
        return "ticket_failed: empty response from github"

    try:
        parsed = json.loads(body)
    except ValueError:
        return f"ticket_failed: non-json response {body}"

    issue_number = parsed.get("number")
    issue_url = parsed.get("html_url")
    if issue_number and issue_url:
        return f"ticket_created: issue #{issue_number} {issue_url}"

    message = parsed.get("message")
    if message:
        return f"ticket_failed: {message}"
    return f"ticket_failed: unexpected github response {parsed}"
