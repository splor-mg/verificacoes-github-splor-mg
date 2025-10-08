#!/usr/bin/env python3
"""
Script para gerenciar o campo "Data Fim" em projetos GitHub.

Este script verifica issues em repositórios e gerencia o campo "Data Fim" 
nos projetos especificados baseado no status do issue.

Regras de negócio:
- Se status != "Done": campo "Data Fim" deve estar vazio
- Se status == "Done" e issue fechado e campo vazio: preencher com data de fechamento do issue
- Se status == "Done" e campo preenchido: manter como está
- Se status == "Done" mas issue não fechado: não preencher campo

Environment variables used:
- GITHUB_TOKEN: GitHub token with write access to Projects v2
- GITHUB_ORG: Organization login (default: splor-mg)

Usage:
  python scripts/issues_close_date.py                                    # Usa projeto do .env ou padrão hardcoded
  python scripts/issues_close_date.py --panel                            # Seleção interativa de projetos
  python scripts/issues_close_date.py --projects "1,2,3"                 # Projetos específicos via argumento
  python scripts/issues_close_date.py --org "minha-org" --verbose        # Organização diferente

Ordem de prioridade para projeto padrão:
  1. Argumento --projects (maior prioridade)
  2. Variável GITHUB_PROJECT_PANEL_DEFAULT no arquivo .env
  3. Valor hardcoded DEFAULT_PROJECT_PANEL (menor prioridade)
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml
from scripts.github_app_auth import get_github_app_installation_token

# Configurações padrão
DEFAULT_ORG = 'splor-mg'
DEFAULT_REPOS_FILE = 'config/repos_list.csv'
DEFAULT_PROJECTS_LIST = 'config/projects-panels-list.yml'
DEFAULT_PROJECT_PANEL = 13  # Número do projeto "Gestão à Vista AID"
DEFAULT_FIELD_NAME = 'Data Fim'

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

def load_dotenv():
    """Carrega variáveis de ambiente do arquivo .env"""
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


def update_projects_data():
    """Chama o script projects_panels.py para atualizar os arquivos de projetos"""
    import subprocess
    import sys
    
    print("🔄 Atualizando dados dos projetos...")
    
    try:
        # Executar o script projects_panels.py
        result = subprocess.run([
            sys.executable, 'scripts/projects_panels.py'
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ Dados dos projetos atualizados com sucesso")
            if result.stdout:
                print(f"📋 Saída do projects_panels.py: {result.stdout}")
            return True
        else:
            print(f"❌ Erro ao atualizar dados dos projetos: {result.stderr}")
            if result.stdout:
                print(f"📋 Saída do projects_panels.py: {result.stdout}")
            return False
    except Exception as e:
        print(f"❌ Erro ao executar projects_panels.py: {e}")
        return False

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

def _iso_date(date_str: str) -> str:
    """Return YYYY-MM-DD from an ISO datetime string."""
    try:
        # GitHub gives ISO 8601 like 2025-08-27T23:59:59Z
        d = dt.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return d.date().isoformat()
    except Exception:
        # If already a date, return as-is
        return date_str[:10]

def load_repos_from_csv(csv_file: str) -> List[Dict[str, Any]]:
    """Carrega a lista de repositórios do arquivo CSV"""
    repos = []
    
    if not os.path.exists(csv_file):
        print(f"❌ Arquivo {csv_file} não encontrado!")
        print("💡 Execute primeiro o script repos_list.py para gerar a lista")
        return repos
    
    print(f"📋 Carregando repositórios de {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            repos.append({
                'name': row['name'], 
                'archived': row.get('archived', 'False') == 'True'
            })
    
    print(f"✅ {len(repos)} repositórios carregados")
    return repos

def load_projects_from_yaml(yaml_file: str) -> List[Dict[str, Any]]:
    """Carrega a lista de projetos do arquivo YAML"""
    projects = []
    
    if not os.path.exists(yaml_file):
        print(f"❌ Arquivo {yaml_file} não encontrado!")
        return projects
    
    print(f"📊 Carregando projetos de {yaml_file}...")
    
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data and 'projects' in data:
                projects = data['projects']
                print(f"✅ {len(projects)} projetos carregados")
            else:
                print("⚠️  Nenhum projeto encontrado no arquivo YAML")
    except yaml.YAMLError as e:
        print(f"❌ Erro ao ler arquivo YAML: {e}")
    
    return projects


def select_panels_interactive(projects_list: List[Dict[str, Any]], field_name: str = DEFAULT_FIELD_NAME) -> List[int]:
    """Interface interativa para seleção de painéis"""
    if not projects_list:
        print("❌ Nenhum projeto disponível para seleção")
        return []
    
    # Criar dicionário para busca rápida por número do projeto
    projects_by_number = {project['number']: project for project in projects_list}
    available_numbers = sorted(projects_by_number.keys())
    
    print("\n📋 Projetos disponíveis:")
    print("=" * 60)
    
    for project_number in available_numbers:
        project = projects_by_number[project_number]
        print(f"num. prj: {project_number}")
        print(f"    name: {project['name']}")
        print(f"      ID: {project['id']}")
        print()
    
    print("=" * 60)
    
    while True:
        try:
            selection = input("Digite o(s) número(s) do(s) projeto(s) que deseja sincronizar (separados por vírgula) ou 'all' para todos: ").strip()
            
            if selection.lower() == 'all':
                selected_projects = []
                for project_number in available_numbers:
                    project = projects_by_number[project_number]
                    # Verificar se o projeto possui o campo especificado
                    has_field = False
                    for field in project.get('fields', []):
                        if field.get('name', '').strip().lower() == field_name.strip().lower():
                            has_field = True
                            break
                    
                    if has_field:
                        selected_projects.append(project_number)
                        print(f"  ✅ Projeto '{project['name']}' (#{project_number}) possui campo '{field_name}'")
                    else:
                        print(f"  ❌ Projeto '{project['name']}' (#{project_number}) NÃO possui campo '{field_name}'")
                
                if not selected_projects:
                    print(f"\n❌ Nenhum dos projetos selecionados possui o campo '{field_name}'")
                    print("💡 Verifique se o campo existe nos projetos ou use um nome de campo diferente")
                    return []
                
                print(f"\n✅ Projetos selecionados: {selected_projects}")
                return selected_projects
            
            # Parse da seleção
            numbers = [int(x.strip()) for x in selection.split(',')]
            
            # Validar números e verificar campos
            valid_numbers = []
            selected_project_names = []
            
            for num in numbers:
                if num in projects_by_number:
                    project = projects_by_number[num]
                    project_name = project['name']
                    
                    # Verificar se o projeto possui o campo especificado
                    has_field = False
                    for field in project.get('fields', []):
                        if field.get('name', '').strip().lower() == field_name.strip().lower():
                            has_field = True
                            break
                    
                    if has_field:
                        valid_numbers.append(num)
                        selected_project_names.append(project_name)
                    else:
                        print(f"❌ Projeto '{project_name}' (#{num}) NÃO possui o campo '{field_name}'")
                        print(f"💡 O processo será interrompido pois o projeto selecionado não tem o campo pretendido")
                        return []
                else:
                    print(f"❌ Número inválido: {num}. Use números de projeto válidos: {', '.join(map(str, available_numbers))}")
                    break
            else:
                if valid_numbers:
                    print(f"✅ Projetos selecionados: {valid_numbers}")
                    for number, name in zip(valid_numbers, selected_project_names):
                        print(f"Projeto selecionado: {number} - {name}")
                    return valid_numbers
                else:
                    print("❌ Nenhum projeto válido selecionado")
                    continue
                    
        except ValueError:
            print("❌ Formato inválido. Use números separados por vírgula (ex: 1,3,5) ou 'all'")
        except KeyboardInterrupt:
            print("\n⏹️  Operação cancelada pelo usuário")
            return []

def filter_projects_by_numbers(projects_list: List[Dict[str, Any]], target_numbers: List[int]) -> List[Dict[str, Any]]:
    """Filtra projetos da lista pelos números especificados"""
    filtered_projects = []
    
    for project in projects_list:
        if project.get('number') in target_numbers:
            filtered_projects.append(project)
            print(f"  ✅ Projeto '{project['name']}' (#{project['number']}) selecionado")
    
    return filtered_projects


def load_projects_with_fields_from_yaml(yaml_file: str, target_numbers: List[int], field_name: str = DEFAULT_FIELD_NAME) -> List[Dict[str, Any]]:
    """Carrega projetos completos do arquivo YAML e filtra pelos números e campo especificados"""
    projects = []
    
    if not os.path.exists(yaml_file):
        print(f"❌ Arquivo {yaml_file} não encontrado!")
        return projects
    
    print(f"📊 Carregando projetos completos de {yaml_file}...")
    
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data and 'projects' in data:
                all_projects = data['projects']
                print(f"🔍 Total de projetos no arquivo: {len(all_projects)}")
                print(f"🎯 Números de projeto solicitados: {target_numbers}")
                print(f"🔍 Campo procurado: '{field_name}'")
                
                # Filtrar pelos números especificados
                for project in all_projects:
                    if project.get('number') in target_numbers:
                        print(f"🔍 Analisando projeto: {project['name']} (#{project['number']})")
                        print(f"   Campos disponíveis: {[f.get('name', 'N/A') for f in project.get('fields', [])]}")
                        
                        # Verificar se possui o campo especificado
                        has_field = False
                        for field in project.get('fields', []):
                            field_name_actual = field.get('name', '').strip()
                            if field_name_actual.lower() == field_name.strip().lower():
                                has_field = True
                                print(f"   ✅ Campo encontrado: '{field_name_actual}' (exato)")
                                break
                        
                        if has_field:
                            projects.append(project)
                            print(f"  ✅ Projeto '{project['name']}' (#{project['number']}) possui campo '{field_name}'")
                        else:
                            print(f"  ⏭️  Projeto '{project['name']}' (#{project['number']}) não possui campo '{field_name}'")
                
                print(f"✅ {len(projects)} projetos carregados e filtrados")
            else:
                print("⚠️  Nenhum projeto encontrado no arquivo YAML")
    except yaml.YAMLError as e:
        print(f"❌ Erro ao ler arquivo YAML: {e}")
    
    return projects

def get_project_field_id(project: Dict[str, Any], field_name: str = DEFAULT_FIELD_NAME) -> Optional[str]:
    """Obtém o ID do campo especificado no projeto"""
    for field in project.get('fields', []):
        if field.get('name', '').strip().lower() == field_name.strip().lower():
            return field['id']
    return None

def get_issues_from_repo(token: str, org: str, repo_name: str) -> List[Dict[str, Any]]:
    """Obtém todos os issues de um repositório"""
    query = """
    query($owner: String!, $repo: String!, $cursor: String) {
      repository(owner: $owner, name: $repo) {
        issues(first: 100, after: $cursor, states: [OPEN, CLOSED]) {
          nodes {
            id
            number
            title
            state
            closedAt
            projectItems(first: 50) {
              nodes {
                id
                project {
                  id
                  number
                  title
                }
                fieldValues(first: 50) {
                  nodes {
                    ... on ProjectV2ItemFieldSingleSelectValue {
                      field {
                        ... on ProjectV2FieldCommon {
                          name
                        }
                      }
                      name
                    }
                    ... on ProjectV2ItemFieldDateValue {
                      field {
                        ... on ProjectV2FieldCommon {
                          name
                        }
                      }
                      date
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
    
    all_issues = []
    cursor = None
    
    while True:
        variables = {"owner": org, "repo": repo_name, "cursor": cursor}
        data = _graphql(token, query, variables)
        
        repository = data.get("repository")
        if not repository:
            break
            
        issues = repository.get("issues", {}).get("nodes", [])
        all_issues.extend(issues)
        
        page_info = repository.get("issues", {}).get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
            
        cursor = page_info.get("endCursor")
    
    return all_issues

def get_project_item_status_and_date(project_item: Dict[str, Any], field_name: str = DEFAULT_FIELD_NAME) -> tuple[Optional[str], Optional[str]]:
    """Obtém o status e a data do campo especificado do item do projeto"""
    status = None
    date_value = None
    
    for field_value in project_item.get('fieldValues', {}).get('nodes', []):
        field = field_value.get('field', {})
        field_name_actual = field.get('name', '')
        
        if field_name_actual.strip().lower() == 'status':
            status = field_value.get('name')
        elif field_name_actual.strip().lower() == field_name.strip().lower():
            date_value = field_value.get('date')
    
    return status, date_value

def clear_date_field(token: str, project_id: str, item_id: str, field_id: str) -> tuple[bool, str]:
    """Limpa o campo de data (define como null)"""
    mutation = """
    mutation($project: ID!, $item: ID!, $field: ID!) {
      updateProjectV2ItemFieldValue(
        input: {
          projectId: $project,
          itemId: $item,
          fieldId: $field,
          value: { date: null }
        }
      ) { clientMutationId }
    }
    """
    
    try:
        _graphql(token, mutation, {"project": project_id, "item": item_id, "field": field_id})
        return True, ""
    except Exception as e:
        error_msg = str(e)
        if "archived and cannot be updated" in error_msg:
            return False, "archived"
        else:
            print(f"      ❌ Erro ao limpar campo: {e}")
            return False, "error"

def set_date_field(token: str, project_id: str, item_id: str, field_id: str, date_value: str) -> tuple[bool, str]:
    """Define o campo de data com o valor especificado"""
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
    
    try:
        _graphql(token, mutation, {
            "project": project_id, 
            "item": item_id, 
            "field": field_id, 
            "value": date_value
        })
        return True, ""
    except Exception as e:
        error_msg = str(e)
        if "archived and cannot be updated" in error_msg:
            return False, "archived"
        else:
            print(f"      ❌ Erro ao definir campo: {e}")
            return False, "error"

def process_issue_for_projects(token: str, issue: Dict[str, Any], target_projects: List[Dict[str, Any]], 
                              field_name: str = DEFAULT_FIELD_NAME) -> Dict[str, int]:
    """Processa um issue para todos os projetos alvo"""
    changes = {"cleared": 0, "set": 0, "errors": 0, "archived_skipped": 0}
    
    issue_number = issue.get('number')
    issue_title = issue.get('title', '')
    issue_state = issue.get('state')
    issue_closed_at = issue.get('closedAt')
    
    print(f"  🔍 Processando issue #{issue_number}: {issue_title[:50]}...")
    
    # Para cada item do projeto associado ao issue
    for project_item in issue.get('projectItems', {}).get('nodes', []):
        project = project_item.get('project', {})
        project_id = project.get('id')
        project_number = project.get('number')
        project_title = project.get('title', '')
        
        # Verificar se este projeto está na lista de projetos alvo
        target_project = None
        for tp in target_projects:
            if tp.get('id') == project_id:
                target_project = tp
                break
        
        if not target_project:
            continue
        
        print(f"    📋 Projeto: {project_title} (#{project_number})")
        
        # Obter ID do campo "Data Fim"
        field_id = get_project_field_id(target_project, field_name)
        if not field_id:
            print(f"      ⚠️  Campo '{field_name}' não encontrado no projeto")
            continue
        
        # Obter status e valor atual do campo
        status, current_date = get_project_item_status_and_date(project_item, field_name)
        
        print(f"      📊 Status: {status}, Data atual: {current_date or 'vazio'}")
        
        # Aplicar regras de negócio
        if status and status.lower() != 'done':
            # Status != "Done": campo deve estar vazio
            if current_date:
                print(f"      🗑️  Limpando campo '{field_name}' (status != Done)")
                success, error_type = clear_date_field(token, project_id, project_item['id'], field_id)
                if success:
                    changes["cleared"] += 1
                    print(f"      ✅ Campo '{field_name}' limpo com sucesso")
                elif error_type == "archived":
                    print(f"      ⏭️  Item arquivado no projeto - ignorando atualização")
                    changes["archived_skipped"] += 1
                else:
                    changes["errors"] += 1
            else:
                print(f"      ✅ Campo '{field_name}' já está vazio")
        
        elif status and status.lower() == 'done':
            # Status == "Done": campo deve ter data de fechamento
            if not current_date and issue_closed_at and issue_state == 'CLOSED':
                date_value = _iso_date(issue_closed_at)
                print(f"      📅 Definindo campo '{field_name}' para {date_value} (status = Done, issue fechado)")
                success, error_type = set_date_field(token, project_id, project_item['id'], field_id, date_value)
                if success:
                    changes["set"] += 1
                    print(f"      ✅ Campo '{field_name}' definido para {date_value}")
                elif error_type == "archived":
                    print(f"      ⏭️  Item arquivado no projeto - ignorando atualização")
                    changes["archived_skipped"] += 1
                else:
                    changes["errors"] += 1
            elif current_date:
                print(f"      ✅ Campo '{field_name}' já está preenchido: {current_date}")
            elif issue_state != 'CLOSED':
                print(f"      ⚠️  Issue com status 'Done' mas não está fechado (state: {issue_state})")
            else:
                print(f"      ⚠️  Issue fechado mas sem data de fechamento")
    
    return changes

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Gerencia o campo 'Data Fim' em projetos GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python scripts/issues_close_date.py                               # Usa projeto do .env ou padrão hardcoded
  python scripts/issues_close_date.py --panel                       # Seleção interativa de projetos
  python scripts/issues_close_date.py --projects "1,2,3"            # Processa apenas projetos específicos (números)
  python scripts/issues_close_date.py --org "minha-org"             # Usa organização diferente
  python scripts/issues_close_date.py --field "Data Conclusão"      # Usa nome de campo diferente
  python scripts/issues_close_date.py --verbose                     # Modo verboso com mais detalhes

Ordem de prioridade para projeto padrão:
  1. Argumento --projects (maior prioridade)
  2. Variável GITHUB_PROJECT_PANEL_DEFAULT no arquivo .env
  3. Valor hardcoded DEFAULT_PROJECT_PANEL (menor prioridade)
        """
    )
    
    parser.add_argument('--panel', 
                       action='store_true',
                       help='Seleção interativa de projetos')
    parser.add_argument('--projects', 
                       help='Projetos específicos (números separados por vírgula)')
    parser.add_argument('--org', 
                       help='Organização para processar (padrão: splor-mg)')
    parser.add_argument('--field', 
                       default=DEFAULT_FIELD_NAME,
                       help=f'Nome do campo de data (padrão: {DEFAULT_FIELD_NAME})')
    parser.add_argument('--repos-file', 
                       default=DEFAULT_REPOS_FILE,
                       help=f'Arquivo CSV com lista de repositórios (padrão: {DEFAULT_REPOS_FILE})')
    parser.add_argument('--projects-list', 
                       default=DEFAULT_PROJECTS_LIST,
                       help=f'Arquivo YAML com lista de projetos (padrão: {DEFAULT_PROJECTS_LIST})')
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='Modo verboso com mais detalhes')
    
    return parser.parse_args()

def main():
    """Função principal"""
    args = parse_arguments()
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Obter token do GitHub via App
    try:
        github_token = get_github_app_installation_token()
    except Exception as e:
        print(f"❌ Falha ao gerar token do GitHub App: {e}")
        return

    print(f"🔑 Usando token (App): {github_token[:8]}...")
    
    # Atualizar dados dos projetos primeiro
    if not update_projects_data():
        print("⚠️  Continuando com dados existentes...")
    
    # Aplicar hierarquia de priorização (argumentos > env vars > padrões)
    org = args.org or os.getenv("GITHUB_ORG") or DEFAULT_ORG
    
    # Mostrar configurações aplicadas
    print(f"\n🔧 Configurações aplicadas:")
    print(f"   Organização: {org}")
    print(f"   Arquivo de repositórios: {args.repos_file}")
    print(f"   Arquivo de projetos: {args.projects_list}")
    print(f"   Campo: {args.field}")
    
    # Mostrar qual valor foi aplicado e de onde veio
    if args.org:
        org_source = "argumento --org"
    elif os.getenv("GITHUB_ORG"):
        org_source = f"arquivo .env (GITHUB_ORG={os.getenv('GITHUB_ORG')})"
    else:
        org_source = f"valor padrão hardcoded (DEFAULT_ORG={DEFAULT_ORG})"
    
    print(f"   Fonte da organização: {org_source}")
    
    if args.verbose:
        print(f"   Modo verboso ativado")
    
    try:
        # Carregar repositórios
        repos = load_repos_from_csv(args.repos_file)
        if not repos:
            print("❌ Nenhum repositório encontrado para processar")
            return
        
        # Carregar lista de projetos (usar projects-panels.yml que tem os campos completos)
        projects_list = load_projects_from_yaml('config/projects-panels.yml')
        if not projects_list:
            print("❌ Nenhum projeto encontrado na lista")
            return
        
        # Determinar quais projetos processar
        target_project_numbers = []
        
        if args.panel:
            # Seleção interativa
            target_project_numbers = select_panels_interactive(projects_list, args.field)
            if not target_project_numbers:
                print("❌ Nenhum projeto selecionado")
                return
        elif args.projects:
            # Projetos específicos via argumento
            try:
                target_project_numbers = [int(p.strip()) for p in args.projects.split(',')]
                print(f"🎯 Projetos especificados via argumento: {target_project_numbers}")
            except ValueError:
                print("❌ Formato inválido para --projects. Use números separados por vírgula")
                return
        else:
            # Seguir ordem de prioridade: .env > hardcoded
            env_panel = os.getenv("GITHUB_PROJECT_PANEL_DEFAULT")
            if env_panel:
                try:
                    target_project_numbers = [int(env_panel)]
                    print(f"🎯 Usando projeto do arquivo .env: {target_project_numbers}")
                except (ValueError, TypeError):
                    print(f"❌ Valor inválido para projeto no .env: {env_panel}")
                    return
            else:
                # Usar valor hardcoded como fallback
                try:
                    target_project_numbers = [int(DEFAULT_PROJECT_PANEL)]
                    print(f"🎯 Usando projeto padrão hardcoded: {target_project_numbers}")
                except (ValueError, TypeError):
                    print(f"❌ Valor inválido para projeto padrão: {DEFAULT_PROJECT_PANEL}")
                    return
        
        # Carregar projetos completos com campos e filtrar
        print(f"\n🔍 Carregando projetos completos e filtrando...")
        projects_with_field = load_projects_with_fields_from_yaml(
            'config/projects-panels.yml', target_project_numbers, args.field
        )
        
        if not projects_with_field:
            print(f"❌ Nenhum projeto encontrado com campo '{args.field}' nos números especificados")
            return
        
        print(f"✅ {len(projects_with_field)} projetos serão processados")
        
        # Processar cada repositório
        total_changes = {"cleared": 0, "set": 0, "errors": 0, "archived_skipped": 0}
        
        for i, repo in enumerate(repos, 1):
            if repo.get('archived', False):
                print(f"\n⏭️  Pulando repositório arquivado: {repo['name']}")
                continue
            
            print(f"\n📁 Repositório {i}/{len(repos)}: {repo['name']}")
            
            try:
                # Obter issues do repositório
                issues = get_issues_from_repo(github_token, org, repo['name'])
                print(f"  📋 {len(issues)} issues encontrados")
                
                # Processar cada issue
                for issue in issues:
                    changes = process_issue_for_projects(
                        github_token, issue, projects_with_field, args.field
                    )
                    
                    # Acumular mudanças
                    for key in total_changes:
                        total_changes[key] += changes[key]
                
                # Pausa entre repositórios para não sobrecarregar a API
                if i < len(repos):
                    print("  ⏳ Aguardando 2 segundos antes do próximo repositório...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ Erro ao processar repositório {repo['name']}: {e}")
                total_changes["errors"] += 1
        
        # Resumo final
        print("\n" + "=" * 60)
        print("🎯 PROCESSAMENTO CONCLUÍDO!")
        print(f"📊 Total de repositórios processados: {len(repos)}")
        print(f"📊 Total de projetos processados: {len(projects_with_field)}")
        print(f"✅ Campos limpos: {total_changes['cleared']}")
        print(f"📅 Campos preenchidos: {total_changes['set']}")
        print(f"⏭️  Itens arquivados ignorados: {total_changes['archived_skipped']}")
        print(f"❌ Erros encontrados: {total_changes['errors']}")
        
        if total_changes["errors"] == 0:
            print("🎉 Todas as operações foram concluídas com sucesso!")
        else:
            print("⚠️  Algumas operações falharam. Verifique os logs acima.")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Operação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
