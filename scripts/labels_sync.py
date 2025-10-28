#!/usr/bin/env python3
"""
Script para sincronizar labels em repositórios GitHub.
Pode sincronizar todos os repositórios de uma organização ou um repositório específico.
"""

import requests
import csv
import yaml
import os
import time
import argparse
from datetime import datetime
from scripts.github_app_auth import get_github_app_installation_token

# Configurações padrão
organization = 'splor-mg'
repos_file = 'config/repos_list.csv'
labels_file = 'config/labels.yaml'

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Sincroniza labels em repositórios GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python labels_sync.py                    # Sincroniza todos os repositórios da organização
  python labels_sync.py --repos repo1,repo2  # Sincroniza repositórios específicos
  python labels_sync.py --org nova-org    # Usa organização diferente
  python labels_sync.py --delete-extras   # Remove labels extras para sincronização completa
        """
    )
    
    parser.add_argument('--repos', 
                       help='Repositórios específicos (CSV ou lista separada por vírgula)')
    parser.add_argument('--org', 
                       help='Organização para sincronizar (padrão: splor-mg)')
    parser.add_argument('--delete-extras', 
                       action='store_true',
                       help='Remove labels extras para manter 100% sincronizado')
    parser.add_argument('--labels', 
                       help='Arquivo YAML com labels (padrão: config/labels.yaml)')
    
    return parser.parse_args()

def load_env():
    """Carrega variáveis de ambiente do arquivo .env"""
    env_file = '.env'
    if os.path.exists(env_file):
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

def load_repos(repos_input, organization):
    """Carrega repositórios de CSV ou lista separada por vírgula"""
    repos = []
    
    if ',' in repos_input:
        # Lista separada por vírgula
        repo_names = [repo.strip() for repo in repos_input.split(',')]
        for repo_name in repo_names:
            # Remove org/ se presente
            if '/' in repo_name:
                repo_name = repo_name.split('/')[-1]
            repos.append({'name': repo_name, 'archived': False})
        print(f"📋 Carregando {len(repos)} repositórios da lista: {repos_input}")
    else:
        # Arquivo CSV
        csv_file = repos_input
        if not os.path.exists(csv_file):
            print(f"❌ Arquivo {csv_file} não encontrado!")
            print("💡 Execute primeiro o script repos_list.py para gerar a lista")
            return repos
        
        print(f"📋 Carregando repositórios de {csv_file}...")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                repos.append({'name': row['name'], 'archived': row.get('archived', 'False') == 'True'})
    
    print(f"✅ {len(repos)} repositórios carregados")
    return repos

def load_repos_from_csv(csv_file):
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
            repos.append({'name': row['name'], 'archived': row.get('archived', 'False') == 'True'})
    
    print(f"✅ {len(repos)} repositórios carregados")
    return repos

def load_labels_from_yaml(yaml_file):
    """Carrega as labels do arquivo YAML"""
    labels = []
    
    if not os.path.exists(yaml_file):
        print(f"❌ Arquivo {yaml_file} não encontrado!")
        return labels
    
    print(f"🏷️  Carregando labels de {yaml_file}...")
    
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data and 'labels' in data:
                labels = data['labels']
                print(f"✅ {len(labels)} labels carregadas")
            else:
                print("⚠️  Nenhuma label encontrada no arquivo YAML")
    except yaml.YAMLError as e:
        print(f"❌ Erro ao ler arquivo YAML: {e}")
    
    return labels

def sync_labels_for_repo(repo_name, labels, token, organization, delete_extras=False):
    """Sincroniza labels para um repositório específico

    Observação: o cabeçalho do repositório (📁 Repositório i/N: <nome>) é impresso pelo chamador.
    Esta função imprime apenas linhas internas com indentação padronizada.
    """
    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    success_count = 0
    error_count = 0
    deleted_count = 0
    created_count = 0
    updated_name_count = 0
    adjusted_color_count = 0
    adjusted_description_count = 0
    unchanged_count = 0
    
    # Primeiro, obter todas as labels atuais do repositório
    print("  📋 Obtendo labels atuais do repositório...")
    current_labels_url = f"https://api.github.com/repos/{organization}/{repo_name}/labels"
    
    try:
        current_response = requests.get(current_labels_url, headers=headers)
        if current_response.status_code == 200:
            current_labels = current_response.json()
            # Criar mapeamento case-insensitive das labels existentes
            current_labels_map = {}
            for label in current_labels:
                current_labels_map[label['name'].lower()] = {
                    'name': label['name'],
                    'color': label['color'],
                    'description': label.get('description', '')
                }
            print(f"    📊 {len(current_labels)} labels encontradas no repositório")
        else:
            print(f"    ❌ Erro ao obter labels atuais: {current_response.status_code}")
            return 0, 0, 1
    except Exception as e:
        print(f"    ❌ Erro ao obter labels atuais: {e}")
        return 0, 0, 1
    
    # Processar cada label do template
    for label in labels:
        label_name = label['name']
        label_color = label['color']
        label_description = label.get('description', '')
        
        print(f"  🏷️  Processando label: {label_name}")
        
        # Verificar se a label já existe (case-insensitive)
        label_name_lower = label_name.lower()
        if label_name_lower in current_labels_map:
            existing_label = current_labels_map[label_name_lower]
            existing_name = existing_label['name']
            existing_color = existing_label['color']
            existing_description = existing_label['description']
            
            # Verificar se precisa atualizar (nome, cor ou descrição)
            needs_update = (
                existing_name != label_name or
                existing_color != label_color or
                existing_description != label_description
            )
            
            if needs_update:
                # Log específico para ajuste de formato
                if existing_name != label_name:
                    print(f"      🔄 Ajustando formato do nome da label: '{existing_name}' → '{label_name}'")
                    updated_name_count += 1
                if existing_color != label_color:
                    adjusted_color_count += 1
                if existing_description != label_description:
                    adjusted_description_count += 1
                
                # Atualizar label existente
                update_url = f"https://api.github.com/repos/{organization}/{repo_name}/labels/{existing_name}"
                update_data = {
                    'name': label_name,
                    'color': label_color,
                    'description': label_description
                }
                
                try:
                    response = requests.patch(update_url, headers=headers, json=update_data)
                    if response.status_code == 200:
                        print(f"      ✅ Label '{label_name}' atualizada com sucesso")
                        success_count += 1
                    else:
                        print(f"      ❌ Erro ao atualizar label '{label_name}': {response.status_code}")
                        error_count += 1
                except Exception as e:
                    print(f"      ❌ Erro ao atualizar label '{label_name}': {e}")
                    error_count += 1
            else:
                print(f"      ✅ Label '{label_name}' já está atualizada")
                success_count += 1
                unchanged_count += 1
        else:
            # Criar nova label
            create_url = f"https://api.github.com/repos/{organization}/{repo_name}/labels"
            create_data = {
                'name': label_name,
                'color': label_color,
                'description': label_description
            }
            
            try:
                response = requests.post(create_url, headers=headers, json=create_data)
                if response.status_code == 201:
                    print(f"      ✅ Label '{label_name}' criada com sucesso")
                    success_count += 1
                    created_count += 1
                else:
                    print(f"      ❌ Erro ao criar label '{label_name}': {response.status_code}")
                    error_count += 1
            except Exception as e:
                print(f"      ❌ Erro ao criar label '{label_name}': {e}")
                error_count += 1
        
        # Pequena pausa para não sobrecarregar a API
        time.sleep(0.1)
    
    # Remover labels extras se habilitado
    if delete_extras:
        print("  🗑️  Verificando labels extras para remoção...")
        
        # Obter labels que não estão no template (case-insensitive)
        template_label_names_lower = {label['name'].lower() for label in labels}
        extra_labels = [name for name in current_labels_map.keys() if name not in template_label_names_lower]
        
        if extra_labels:
            print(f"    📋 {len(extra_labels)} labels extras encontradas para remoção")
            
            for extra_label_name_lower in extra_labels:
                extra_label_name = current_labels_map[extra_label_name_lower]['name']
                delete_url = f"https://api.github.com/repos/{organization}/{repo_name}/labels/{extra_label_name}"
                
                try:
                    response = requests.delete(delete_url, headers=headers)
                    if response.status_code == 204:
                        print(f"      🗑️  Label '{extra_label_name}' removida com sucesso")
                        deleted_count += 1
                    else:
                        print(f"      ❌ Erro ao remover label '{extra_label_name}': {response.status_code}")
                        error_count += 1
                    
                    # Pequena pausa para não sobrecarregar a API
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"      ❌ Erro ao remover label '{extra_label_name}': {e}")
                    error_count += 1
        else:
            print("    ✅ Nenhuma label extra encontrada para remoção")
    else:
        print("  ⏭️  Remoção de labels extras desabilitada")
    
    print(f"  📊 Resumo: {success_count} labels processadas, {deleted_count} deletadas, {error_count} erros")
    details = {
        'processed': success_count + error_count,  # aproximação
        'created': created_count,
        'updated_name': updated_name_count,
        'adjusted_color': adjusted_color_count,
        'adjusted_description': adjusted_description_count,
        'deleted': deleted_count,
        'unchanged': unchanged_count,
        'errors': error_count,
    }
    return success_count, deleted_count, error_count, details

def sync_single_repo(repo_full_name, labels, token, delete_extras=False):
    """Sincroniza labels para um repositório específico (formato: org/repo)"""
    if '/' not in repo_full_name:
        print(f"❌ Formato inválido: {repo_full_name}. Use: org/repo")
        return False
    
    org, repo = repo_full_name.split('/', 1)
    print(f"🎯 Sincronizando repositório específico: {org}/{repo}")
    
    success, deleted, errors = sync_labels_for_repo(repo, labels, token, org, delete_extras)
    
    if errors == 0:
        print(f"✅ Labels sincronizadas com sucesso para {org}/{repo}")
        return True
    else:
        print(f"⚠️  Sincronização concluída com {errors} erros para {org}/{repo}")
        return False

def main():
    # Parse arguments
    args = parse_arguments()
    
    # Carregar variáveis de ambiente
    load_env()
    
    # Obter token do GitHub via App
    try:
        github_token = get_github_app_installation_token()
        print(f"🔑 Usando token (App): {github_token[:8]}...")
    except Exception as e:
        print(f"❌ Falha ao gerar token do GitHub App: {e}")
        return
    
    # Configurar parâmetros baseado nos argumentos
    if args.org:
        organization = args.org
    if args.labels:
        labels_file = args.labels
    
    # Carregar labels
    labels = load_labels_from_yaml(labels_file)
    if not labels:
        return
    
    # Se foi especificado repositórios específicos
    if args.repos:
        repos = load_repos(args.repos, organization)
        if not repos:
            return
        print(f"🎯 Sincronizando {len(repos)} repositórios específicos")
    else:
        # Carregar repositórios do CSV padrão
        repos = load_repos(repos_file, organization)
        if not repos:
            return
    
    print(f"\n🚀 Iniciando sincronização de labels para {len(repos)} repositórios...")
    print("=" * 60)
    
    total_success = 0
    total_deleted = 0
    total_errors = 0
    
    # Processar cada repositório
    for i, repo in enumerate(repos, 1):
        print(f"\n📁 Repositório {i}/{len(repos)}")
        
        success, deleted, errors = sync_labels_for_repo(repo, labels, github_token, organization, args.delete_extras)
        total_success += success
        total_deleted += deleted
        total_errors += errors
        
        # Pausa entre repositórios para não sobrecarregar a API
        if i < len(repos):
            print("  ⏳ Aguardando 2 segundos antes do próximo repositório...")
            time.sleep(2)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("🎯 SINCRONIZAÇÃO CONCLUÍDA!")
    print(f"📊 Total de repositórios processados: {len(repos)}")
    print(f"✅ Labels processadas com sucesso: {total_success}")
    print(f"🗑️  Labels deletadas: {total_deleted}")
    print(f"❌ Erros encontrados: {total_errors}")
    
    if total_errors == 0:
        print("🎉 Todas as labels foram sincronizadas com sucesso!")
        if args.delete_extras and total_deleted > 0:
            print(f"🗑️  {total_deleted} labels extras foram removidas para manter consistência")
        elif not args.delete_extras:
            print("🛡️  Modo conservador: labels extras foram preservadas")
    else:
        print("⚠️  Algumas labels tiveram problemas. Verifique os logs acima.")
    
    print(f"\n💡 Verifique os repositórios em: https://github.com/{organization}")

if __name__ == "__main__":
    main()
