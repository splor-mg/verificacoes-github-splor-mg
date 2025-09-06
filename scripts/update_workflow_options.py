#!/usr/bin/env python3
"""
Script para atualizar o workflow GitHub Actions com opções dinâmicas de projetos.

Este script lê o arquivo projects-panels-list.yml e atualiza o workflow
issues-close-date.yml com as opções de projetos atuais.
"""

import yaml
import re
from pathlib import Path


def load_projects_list(yaml_file: str = 'docs/projects-panels-list.yml'):
    """Carrega a lista de projetos do arquivo YAML"""
    if not Path(yaml_file).exists():
        print(f"❌ Arquivo {yaml_file} não encontrado!")
        return []
    
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('projects', [])
    except yaml.YAMLError as e:
        print(f"❌ Erro ao ler arquivo YAML: {e}")
        return []


def generate_project_options(projects):
    """Gera as opções de projetos no formato do GitHub Actions"""
    options = []
    
    # Adicionar projeto padrão primeiro (se não estiver na lista)
    default_project = "13 - Gestão à Vista AID"
    if not any("13 - Gestão à Vista AID" in f"{p['number']} - {p['name']}" for p in projects):
        options.append(f'          - "{default_project}"')
    
    # Adicionar projetos da lista
    for project in sorted(projects, key=lambda x: x['number']):
        option = f"{project['number']} - {project['name']}"
        options.append(f'          - "{option}"')
    
    return options


def update_workflow_file(workflow_file: str, new_options: list):
    """Atualiza o arquivo de workflow com as novas opções"""
    if not Path(workflow_file).exists():
        print(f"❌ Arquivo {workflow_file} não encontrado!")
        return False
    
    # Ler o arquivo atual
    with open(workflow_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a seção de opções do project_number
    pattern = r'(project_number:\s*\n\s*description:.*?\n\s*required:.*?\n\s*default:.*?\n\s*type: choice\s*\n\s*options:\s*\n)(.*?)(\s*field_name:)'
    
    def replace_options(match):
        prefix = match.group(1)
        suffix = match.group(3)
        new_options_text = '\n'.join(new_options) + '\n'
        return prefix + new_options_text + suffix
    
    # Aplicar a substituição
    new_content = re.sub(pattern, replace_options, content, flags=re.DOTALL)
    
    if new_content == content:
        print("⚠️  Nenhuma alteração necessária no workflow")
        return True
    
    # Salvar o arquivo atualizado
    with open(workflow_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Workflow {workflow_file} atualizado com sucesso!")
    return True


def main():
    """Função principal"""
    print("🔄 Atualizando opções de projetos no workflow...")
    
    # Carregar projetos
    projects = load_projects_list()
    if not projects:
        print("❌ Nenhum projeto encontrado!")
        return False
    
    print(f"✅ {len(projects)} projetos encontrados")
    
    # Gerar opções
    options = generate_project_options(projects)
    
    print("\n📋 Novas opções de projetos:")
    for option in options:
        print(f"  {option}")
    
    # Atualizar workflow
    workflow_file = '.github/workflows/issues-close-date.yml'
    if update_workflow_file(workflow_file, options):
        print(f"\n🎉 Workflow atualizado com sucesso!")
        print("💡 As opções de projetos agora são dinâmicas baseadas em projects-panels-list.yml")
        return True
    else:
        print("❌ Erro ao atualizar workflow")
        return False


if __name__ == "__main__":
    main()
