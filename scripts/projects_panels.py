#!/usr/bin/env python3
"""
Extract GitHub ProjectV2 information and export to YAML format.

This script queries the GitHub GraphQL API to extract all projects from an organization
and their field definitions, then exports them to a YAML file with the same structure
as projects-panels.yml.

Environment variables used:
- GITHUB_TOKEN: GitHub token with read access to Projects v2
- GITHUB_ORG: Organization login (default: aid-pilot)

Usage:
  python scripts/projects_panels.py
  python scripts/projects_panels.py --org "organization-name"
  python scripts/projects_panels.py --output "custom-output.yml"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml

# Load environment variables from .env file
def load_dotenv():
    """Load environment variables from .env file."""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load .env at module level
load_dotenv()


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


def _require_env(name: str) -> str:
    """Get required environment variable or raise error."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _graphql(token: str, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    """Execute GraphQL query against GitHub API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.post(
        GITHUB_GRAPHQL_URL, 
        json={"query": query, "variables": variables}, 
        headers=headers
    )
    if resp.status_code != 200:
        raise RuntimeError(f"GraphQL HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {json.dumps(data['errors'], ensure_ascii=False)}")
    return data["data"]


def get_organization_projects(token: str, org: str) -> List[Dict[str, Any]]:
    """Get all projects from an organization."""
    query = """
    query($org: String!, $cursor: String) {
      organization(login: $org) {
        projectsV2(first: 100, after: $cursor) {
          nodes {
            id
            number
            title
            shortDescription
            fields(first: 100) {
              nodes {
                ... on ProjectV2Field {
                  id
                  name
                  dataType
                }
                ... on ProjectV2SingleSelectField {
                  id
                  name
                  dataType
                  options {
                    id
                    name
                    description
                    color
                  }
                }
                ... on ProjectV2IterationField {
                  id
                  name
                  dataType
                  configuration {
                    iterations {
                      id
                      title
                      startDate
                    }
                  }
                }

              }
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
    """
    
    all_projects = []
    cursor = None
    
    while True:
        variables = {"org": org, "cursor": cursor}
        data = _graphql(token, query, variables)
        
        projects = data["organization"]["projectsV2"]["nodes"]
        all_projects.extend(projects)
        
        page_info = data["organization"]["projectsV2"]["pageInfo"]
        if not page_info["hasNextPage"]:
            break
            
        cursor = page_info["endCursor"]
    
    return all_projects


def format_field_for_yaml(field: Dict[str, Any]) -> Dict[str, Any]:
    """Format a field for YAML output."""
    formatted = {
        "name": field["name"],
        "id": field["id"],
        "dataType": field["dataType"]
    }
    
    # Add options for single select fields
    if field["dataType"] == "SINGLE_SELECT" and "options" in field:
        formatted["options"] = []
        for option in field["options"]:
            formatted["options"].append({
                "name": option["name"],
                "description": option.get("description", ""),
                "color": option.get("color", "")
            })
    
    # Add iterations for iteration fields
    elif field["dataType"] == "ITERATION" and "configuration" in field:
        if field["configuration"] and "iterations" in field["configuration"]:
            formatted["iterations"] = []
            for iteration in field["configuration"]["iterations"]:
                formatted["iterations"].append({
                    "id": iteration["id"],
                    "title": iteration["title"],
                    "startDate": iteration.get("startDate", ""),
                    "endDate": iteration.get("endDate", "")
                })
    
    return formatted


def projects_to_yaml_structure(projects: List[Dict[str, Any]], org: str) -> Dict[str, Any]:
    """Convert projects data to YAML structure."""
    yaml_structure = {
        "org": org,
        "projects": []
    }
    
    for project in projects:
        project_entry = {
            "name": project["title"],
            "number": project["number"],
            "id": project["id"],
            "fields": []
        }
        
        # Add short description if available
        if project.get("shortDescription"):
            project_entry["description"] = project["shortDescription"]
        
        # Process fields
        for field in project["fields"]["nodes"]:
            formatted_field = format_field_for_yaml(field)
            project_entry["fields"].append(formatted_field)
        
        yaml_structure["projects"].append(project_entry)
    
    return yaml_structure


def save_yaml(data: Dict[str, Any], output_path: str) -> None:
    """Save data to YAML file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ YAML salvo em: {output_path}")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract GitHub ProjectV2 information and export to YAML"
    )
    parser.add_argument(
        "--org", 
        default=os.getenv("GITHUB_ORG", "aid-pilot"),
        help="Organization login (default: GITHUB_ORG env var or 'aid-pilot')"
    )
    parser.add_argument(
        "--output", 
        default="docs/projects-panels.yml",
        help="Output YAML file path (default: docs/projects-panels.yml)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Verbose output"
    )
    return parser.parse_args()


def main() -> None:
    """Main function."""
    args = parse_args()
    
    # Get GitHub token
    token = os.getenv("GITHUB_TOKEN") or _require_env("GITHUB_TOKEN")
    
    if args.verbose:
        print(f"🔍 Extraindo projetos da organização: {args.org}")
        print(f"📁 Arquivo de saída: {args.output}")
    
    try:
        # Get all projects from organization
        print(f"📊 Buscando projetos da organização '{args.org}'...")
        projects = get_organization_projects(token, args.org)
        
        if not projects:
            print(f"⚠️  Nenhum projeto encontrado na organização '{args.org}'")
            return
        
        print(f"✅ Encontrados {len(projects)} projetos")
        
        # Convert to YAML structure
        yaml_data = projects_to_yaml_structure(projects, args.org)
        
        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to YAML file
        save_yaml(yaml_data, str(output_path))
        
        # Print summary
        print(f"\n📋 Resumo da extração:")
        print(f"   Organização: {args.org}")
        print(f"   Total de projetos: {len(projects)}")
        
        total_fields = sum(len(p["fields"]) for p in yaml_data["projects"])
        print(f"   Total de campos: {total_fields}")
        
        for project in yaml_data["projects"]:
            print(f"   - {project['name']} (#{project['number']}): {len(project['fields'])} campos")
        
    except Exception as e:
        print(f"❌ Erro durante a extração: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
