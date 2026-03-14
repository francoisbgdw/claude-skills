"""
Fabric REST API helper functions.

Usage from Claude Code skills:
    python -c "from fabric_helpers import *; print(list_workspaces())"

Requires: azure-identity package and az login authentication.
"""

import json
import subprocess
from typing import Optional


def _az_rest(method: str, url: str, body: Optional[dict] = None) -> dict:
    """Execute an az rest command and return parsed JSON."""
    cmd = ["az", "rest", "--method", method, "--url", url]
    if body:
        cmd.extend(["--body", json.dumps(body)])
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout) if result.stdout.strip() else {}


BASE = "https://api.fabric.microsoft.com/v1"


def list_workspaces() -> list[dict]:
    """List all Fabric workspaces accessible to the current user."""
    resp = _az_rest("GET", f"{BASE}/workspaces")
    return resp.get("value", [])


def list_items(workspace_id: str, item_type: Optional[str] = None) -> list[dict]:
    """List items in a workspace, optionally filtered by type."""
    url = f"{BASE}/workspaces/{workspace_id}/items"
    if item_type:
        url += f"?type={item_type}"
    resp = _az_rest("GET", url)
    return resp.get("value", [])


def list_lakehouses(workspace_id: str) -> list[dict]:
    """List lakehouses in a workspace."""
    return list_items(workspace_id, "Lakehouse")


def list_tables(workspace_id: str, lakehouse_id: str) -> list[dict]:
    """List tables in a lakehouse."""
    resp = _az_rest("GET", f"{BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/tables")
    return resp.get("value", [])


def refresh_semantic_model(workspace_id: str, model_id: str) -> dict:
    """Trigger a refresh on a semantic model."""
    return _az_rest("POST", f"{BASE}/workspaces/{workspace_id}/semanticModels/{model_id}/refresh")


def get_refresh_history(workspace_id: str, model_id: str) -> list[dict]:
    """Get refresh history for a semantic model."""
    resp = _az_rest("GET", f"{BASE}/workspaces/{workspace_id}/semanticModels/{model_id}/refreshes")
    return resp.get("value", [])


def run_pipeline(workspace_id: str, pipeline_id: str) -> dict:
    """Trigger a data pipeline run."""
    return _az_rest("POST", f"{BASE}/workspaces/{workspace_id}/items/{pipeline_id}/jobs/instances?jobType=Pipeline")


def get_job_status(workspace_id: str, item_id: str) -> list[dict]:
    """Get job instances for an item."""
    resp = _az_rest("GET", f"{BASE}/workspaces/{workspace_id}/items/{item_id}/jobs/instances")
    return resp.get("value", [])


def git_status(workspace_id: str) -> dict:
    """Get git sync status for a workspace."""
    return _az_rest("GET", f"{BASE}/workspaces/{workspace_id}/git/status")


if __name__ == "__main__":
    # Quick test: list workspaces
    workspaces = list_workspaces()
    for ws in workspaces:
        print(f"{ws.get('displayName', 'N/A')} ({ws.get('id', 'N/A')})")
