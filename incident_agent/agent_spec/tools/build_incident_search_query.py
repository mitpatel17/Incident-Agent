from __future__ import annotations

from ibm_watsonx_orchestrate.agent_builder.tools import ToolPermission, tool


@tool(permission=ToolPermission.READ_ONLY)
def build_incident_search_query(
    service: str,
    environment: str,
    symptoms_error: str,
    time_window: str,
    user_impact: str,
    recent_changes: str,
) -> str:
    """
    Build a focused knowledge-base search query from incident form fields.
    """
    parts = [
        f"service={service.strip()}",
        f"environment={environment.strip()}",
        f"symptoms={symptoms_error.strip()}",
        f"time_window={time_window.strip()}",
        f"user_impact={user_impact.strip()}",
        f"recent_changes={recent_changes.strip()}",
    ]
    return " | ".join(parts)
