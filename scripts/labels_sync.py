#!/usr/bin/env python3
"""
Script para sincronizar labels em todos os repositórios de uma organização GitHub.
Lê a lista de repositórios do arquivo docs/repos_list.csv e aplica as labels
definidas em docs/labels.yaml.
"""

import requests
import csv
import yaml
import os
import time
from datetime import datetime

# Configurações caso 
organization = 'splor-mg'
repos_file = 'docs/repos_list.csv'
labels_file = 'docs/labels.yaml'

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
            repos.append(row['name'])
    
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

def sync_labels_for_repo(repo_name, labels, token, organization, delete_extras=True):
    """Sincroniza labels para um repositório específico"""
    print(f"\n🔄 Processando repositório: {organization}/{repo_name}")
    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    success_count = 0
    error_count = 0
    deleted_count = 0
    
    # Primeiro, obter todas as labels atuais do repositório
    print("  📋 Obtendo labels atuais do repositório...")
    current_labels_url = f"https://api.github.com/repos/{organization}/{repo_name}/labels"
    
    try:
        current_response = requests.get(current_labels_url, headers=headers)
        if current_response.status_code == 200:
            current_labels = current_response.json()
            current_label_names = {label['name'] for label in current_labels}
            print(f"    📊 {len(current_labels)} labels encontradas no repositório")
        else:
            print(f"    ❌ Erro ao obter labels atuais: {current_response.status_code}")
            return 0, 0, 1
    except Exception as e:
        print(f"    ❌ Erro ao obter labels atuais: {e}")
        return 0, 0, 1
    
    # Processar cada label do arquivo YAML
    for label in labels:
        label_name = label['name']
        label_color = label['color']
        label_description = label.get('description', '')
        
        print(f"  🏷️  Processando label: {label_name}")
        
        try:
            # Tentar atualizar a label existente
            update_url = f"https://api.github.com/repos/{organization}/{repo_name}/labels/{label_name}"
            update_data = {
                'color': label_color,
                'description': label_description
            }
            
            response = requests.patch(update_url, headers=headers, json=update_data)
            
            if response.status_code == 200:
                print(f"      ✅ Label '{label_name}' atualizada com sucesso")
                success_count += 1
            elif response.status_code == 404:
                # Label não existe, criar nova
                create_url = f"https://api.github.com/repos/{organization}/{repo_name}/labels"
                create_data = {
                    'name': label_name,
                    'color': label_color,
                    'description': label_description
                }
                
                create_response = requests.post(create_url, headers=headers, json=create_data)
                
                if create_response.status_code == 201:
                    print(f"      ✅ Label '{label_name}' criada com sucesso")
                    success_count += 1
                else:
                    print(f"      ❌ Erro ao criar label '{label_name}': {create_response.status_code}")
                    error_count += 1
            else:
                print(f"      ❌ Erro ao atualizar label '{label_name}': {response.status_code}")
                error_count += 1
                
        except Exception as e:
            print(f"      ❌ Erro ao processar label '{label_name}': {e}")
            error_count += 1
        
        # Pequena pausa para não sobrecarregar a API
        time.sleep(0.1)
    
    # Identificar e deletar labels extras que não estão no arquivo YAML
    if delete_extras:
        print("  🗑️  Verificando labels extras para remoção...")
        yaml_label_names = {label['name'] for label in labels}
        labels_to_delete = current_label_names - yaml_label_names
        
        if labels_to_delete:
            print(f"    📋 {len(labels_to_delete)} labels extras encontradas para remoção")
            
            for extra_label_name in labels_to_delete:
                try:
                    delete_url = f"https://api.github.com/repos/{organization}/{repo_name}/labels/{extra_label_name}"
                    delete_response = requests.delete(delete_url, headers=headers)
                    
                    if delete_response.status_code == 204:
                        print(f"      🗑️  Label '{extra_label_name}' removida com sucesso")
                        deleted_count += 1
                    else:
                        print(f"      ❌ Erro ao remover label '{extra_label_name}': {delete_response.status_code}")
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
    return success_count, deleted_count, error_count

def sync_repository_labels(organization, repo_name, token, labels_file, delete_extras=True):
    """Sincroniza labels para um repositório específico"""
    print(f"🔄 Sincronizando labels para repositório: {organization}/{repo_name}")
    
    # Carregar labels do arquivo YAML
    labels = load_labels_from_yaml(labels_file)
    if not labels:
        print("❌ Não foi possível carregar as labels do arquivo YAML")
        return False
    
    # Sincronizar labels para o repositório
    success, deleted, errors = sync_labels_for_repo(repo_name, labels, token, organization, delete_extras)
    
    if errors == 0:
        print(f"✅ Labels sincronizadas com sucesso para {organization}/{repo_name}")
        return True
    else:
        print(f"⚠️  Sincronização concluída com {errors} erros para {organization}/{repo_name}")
        return False

def main():
    # Carregar variáveis de ambiente
    load_env()
    
    # Obter token do GitHub
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("❌ GITHUB_TOKEN não encontrado!")
        print("💡 Certifique-se de que o arquivo .env contém: GITHUB_TOKEN=seu_token_aqui")
        return
    
    print(f"🔑 Usando token: {github_token[:8]}...")
    
    # Carregar repositórios
    repos = load_repos_from_csv(repos_file)
    if not repos:
        return
    
    # Carregar labels
    labels = load_labels_from_yaml(labels_file)
    if not labels:
        return
    
    print(f"\n🚀 Iniciando sincronização de labels para {len(repos)} repositórios...")
    print("=" * 60)
    
    total_success = 0
    total_deleted = 0
    total_errors = 0
    
    # Processar cada repositório
    for i, repo in enumerate(repos, 1):
        print(f"\n📁 Repositório {i}/{len(repos)}")
        
        success, deleted, errors = sync_labels_for_repo(repo, labels, github_token, organization, delete_extras=True)
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
        if total_deleted > 0:
            print(f"🗑️  {total_deleted} labels extras foram removidas para manter consistência")
    else:
        print("⚠️  Algumas labels tiveram problemas. Verifique os logs acima.")
    
    print(f"\n💡 Verifique os repositórios em: https://github.com/{organization}")

if __name__ == "__main__":
    main()
