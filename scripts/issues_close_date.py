#!/usr/bin/env python3
"""
Synchronize GitHub Project (v2) date field when an Issue is closed.

This script is intended to be executed from a GitHub Actions workflow when an
issue is closed. It finds the corresponding Project item for the closed issue
in the specified Organization Project and sets a Date field (e.g. "Data Fim")
to the issue's closed_at date.

Inputs are passed via CLI flags or environment variables for easier use in CI.

Environment variables used (fallbacks for CLI flags):
- GITHUB_TOKEN: GitHub token with write access to Projects v2
- GITHUB_ORG: Organization login

Example (GitHub Actions):
  poetry run python scripts/issues_sync.py \
    --org "$ORG" \
    --project-number 13 \
    --field-name "Data Fim" \
    --issue-node-id "$ISSUE_NODE_ID" \
    --closed-at "$ISSUE_CLOSED_AT"
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from typing import Any, Dict, Optional

import requests


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _graphql(token: str, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.post(GITHUB_GRAPHQL_URL, json={"query": query, "variables": variables}, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f"GraphQL HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {json.dumps(data['errors'], ensure_ascii=False)}")
    return data["data"]


def _iso_date(date_str: str) -> str:
    """Return YYYY-MM-DD from an ISO datetime string."""
    try:
        # GitHub gives ISO 8601 like 2025-08-27T23:59:59Z
        d = dt.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return d.date().isoformat()
    except Exception:
        # If already a date, return as-is
        return date_str[:10]


def get_project_and_field_ids(token: str, org: str, project_number: int, field_name: str) -> tuple[str, str]:
    query = """
    query($org: String!, $number: Int!) {
      organization(login: $org) {
        projectV2(number: $number) {
          id
          fields(first: 100) {
            nodes { id name dataType }
          }
        }
      }
    }
    """
    data = _graphql(token, query, {"org": org, "number": project_number})
    project = data["organization"]["projectV2"]
    if not project:
        raise RuntimeError(f"Project not found: {org} #{project_number}")
    project_id = project["id"]
    field_id = None
    for f in project["fields"]["nodes"]:
        if f["name"].strip().lower() == field_name.strip().lower():
            field_id = f["id"]
            break
    if not field_id:
        raise RuntimeError(f"Field '{field_name}' not found in project {org} #{project_number}")
    return project_id, field_id


def get_or_find_project_item_id_for_issue(token: str, issue_node_id: str, project_id: str) -> Optional[str]:
    """Return the ProjectV2Item id for the issue in the given project, if it exists.

    We inspect the issue's project items and pick the one belonging to the
    specified project. If none exists, returns None.
    """
    query = """
    query($id: ID!) {
      node(id: $id) {
        ... on Issue {
          projectItems: projectV2Items(first: 50) {
            nodes { id project { id } }
          }
        }
      }
    }
    """
    data = _graphql(token, query, {"id": issue_node_id})
    items = data["node"].get("projectItems", {}).get("nodes", [])
    for item in items:
        proj = item.get("project")
        if proj and proj.get("id") == project_id:
            return item["id"]
    return None


def update_date_field(token: str, project_id: str, item_id: str, field_id: str, date_value: str) -> None:
    mutation = """
    mutation($project: ID!, $item: ID!, $field: ID!, $value: Date!) {
      updateProjectV2ItemFieldValue(
        input: {
          projectId: $project,
          itemId: $item,
          fieldId: $field,
          value: { date: $value }
        }
      ) { clientMutationId }
    }
    """
    _graphql(token, mutation, {"project": project_id, "item": item_id, "field": field_id, "value": date_value})


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Set a Project v2 Date field when an issue closes")
    p.add_argument("--org", default=os.getenv("GITHUB_ORG"), help="Organization login (fallback: GITHUB_ORG)")
    p.add_argument("--project-number", type=int, required=True, help="Project number (as in URL)")
    p.add_argument("--field-name", default="Data Fim", help="Project field name to set (default: Data Fim)")
    p.add_argument("--issue-node-id", required=True, help="Issue node_id from the webhook payload")
    p.add_argument("--closed-at", required=True, help="Issue closed_at timestamp from the webhook payload")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    token = os.getenv("GITHUB_TOKEN") or _require_env("GITHUB_TOKEN")
    if not args.org:
        raise RuntimeError("Organization not provided. Use --org or set GITHUB_ORG.")

    date_value = _iso_date(args.closed_at)

    project_id, field_id = get_project_and_field_ids(token, args.org, args.project_number, args.field_name)

    item_id = get_or_find_project_item_id_for_issue(token, args.issue_node_id, project_id)
    if not item_id:
        print("⚠️  Issue is not linked to the specified Project. Nothing to update.")
        return

    update_date_field(token, project_id, item_id, field_id, date_value)
    print(f"✅ Field '{args.field_name}' updated to {date_value} for the linked Project item.")


if __name__ == "__main__":
    main()


