#!/usr/bin/env python3
"""
Extract GitHub ProjectV2 information and export to YAML format.

This script queries the GitHub GraphQL API to extract all projects from an organization
and their field definitions, then exports them to a YAML file with the same structure
as projects-panels.yml.

Environment variables used:
- GITHUB_TOKEN: GitHub token with read access to Projects v2
- GITHUB_ORG: Organization login (default: splor-mg)

Usage:
  python scripts/projects_panels.py
  python scripts/projects_panels.py --org "organization-name"
  python scripts/projects_panels.py --output "custom-output.yml"

Priorização de configuração:
1. Argumento --org (maior prioridade)
2. Variável GITHUB_ORG no arquivo .env
3. Valor padrão hardcoded: splor-mg (menor prioridade)
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

# Configurações padrão
DEFAULT_ORG = 'splor-mg'
DEFAULT_OUTPUT = 'docs/projects-panels.yml'
DEFAULT_LIST_OUTPUT = 'docs/projects-panels-list.yml'

# Load environment variables from .env file
def load_dotenv():
    """Load environment variables from .env file."""
    env_file = Path('.env')
    if env_file.exists():
        print(f"📁 Carregando variáveis de {env_file}...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Variáveis de ambiente carregadas")
    else:
        print(f"⚠️  Arquivo {env_file} não encontrado")


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


def projects_to_list_structure(projects: List[Dict[str, Any]], org: str) -> Dict[str, Any]:
    """Convert projects data to simple list structure with numbers, names and IDs."""
    list_structure = {
        "org": org,
        "projects": []
    }
    
    for project in projects:
        project_entry = {
            "number": project["number"],
            "name": project["title"],
            "id": project["id"]
        }
        list_structure["projects"].append(project_entry)
    
    return list_structure


def save_yaml(data: Dict[str, Any], output_path: str) -> None:
    """Save data to YAML file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ YAML salvo em: {output_path}")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract GitHub ProjectV2 information and export to YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python scripts/projects_panels.py                               # Extrai projetos da organização padrão (splor-mg)
  python scripts/projects_panels.py --org "minha-org"             # Extrai projetos de organização específica
  python scripts/projects_panels.py --output "meus_projetos.yml"  # Arquivo de saída customizado
  python scripts/projects_panels.py --list-output "lista.yml"     # Arquivo de lista customizado
  python scripts/projects_panels.py --verbose                     # Modo verboso com mais detalhes
        """
    )
    parser.add_argument(
        "--org", 
        help=f"Organization login (padrão: GITHUB_ORG env var ou '{DEFAULT_ORG}')"
    )
    parser.add_argument(
        "--output", 
        help=f"Output YAML file path (padrão: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "--list-output", 
        help=f"Output list YAML file path (padrão: {DEFAULT_LIST_OUTPUT})"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Modo verboso com mais detalhes"
    )
    return parser.parse_args()


def main() -> None:
    """Main function."""
    args = parse_args()
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Get GitHub token
    token = os.getenv("GITHUB_TOKEN") or _require_env("GITHUB_TOKEN")
    
    # Aplicar hierarquia de priorização (argumentos > env vars > padrões)
    # 1. Argumentos da linha de comando (maior prioridade)
    # 2. Variáveis de ambiente (prioridade média)
    # 3. Valores padrão (menor prioridade)
    
    org = args.org or os.getenv("GITHUB_ORG") or DEFAULT_ORG
    output = args.output or DEFAULT_OUTPUT
    list_output = args.list_output or DEFAULT_LIST_OUTPUT
    
    if args.verbose:
        print(f"🔍 Extraindo projetos da organização: {org}")
        print(f"📁 Arquivo de saída: {output}")
        print(f"📋 Arquivo de lista: {list_output}")
        print(f"🔧 Configurações aplicadas:")
        print(f"   Organização: {org}")
        print(f"   Arquivo de saída: {output}")
        print(f"   Arquivo de lista: {list_output}")
        print(f"   Token: {token[:8]}...")
    
    try:
        # Get all projects from organization
        print(f"📊 Buscando projetos da organização '{org}'...")
        projects = get_organization_projects(token, org)
        
        if not projects:
            print(f"⚠️  Nenhum projeto encontrado na organização '{org}'")
            return
        
        print(f"✅ Encontrados {len(projects)} projetos")
        
        # Convert to YAML structure
        yaml_data = projects_to_yaml_structure(projects, org)
        list_data = projects_to_list_structure(projects, org)
        
        # Ensure output directories exist
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        list_output_path = Path(list_output)
        list_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to YAML files
        save_yaml(yaml_data, str(output_path))
        save_yaml(list_data, str(list_output_path))
        
        # Print summary
        print(f"\n📋 Resumo da extração:")
        print(f"   Organização: {org}")
        print(f"   Total de projetos: {len(projects)}")
        print(f"   Arquivo completo: {output}")
        print(f"   Arquivo de lista: {list_output}")
        
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
