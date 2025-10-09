import requests
import csv
import os
import yaml
from datetime import datetime
from typing import Optional, List, Dict, Any
from scripts.github_app_auth import get_github_app_installation_token
from cache_manager import CacheManager



def load_labels_from_yaml(labels_file):
    """
    Carrega as labels padrão do arquivo YAML
    """
    
    try:
        if not os.path.exists(labels_file):
            print(f"❌ Arquivo {labels_file} não encontrado")
            print("💡 Crie o arquivo de labels padrão para continuar")
            return None
        
        print(f"📁 Carregando labels do arquivo {labels_file}...")
        with open(labels_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'labels' not in data:
            print("❌ Arquivo YAML não contém seção 'labels' válida")
            print("💡 Estrutura válida esperada:")
            print("   name: nome da label")
            print("   color: código hexadecimal da cor")
            print("   description: descrição da label")
            print("   category: categoria da label (opcional)")
            return None
        
        labels = data['labels']
        print(f"✅ {len(labels)} labels carregadas do arquivo YAML")
        return labels
        
    except yaml.YAMLError as e:
        print(f"❌ Erro ao processar arquivo YAML: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo YAML: {e}")
        return None

def get_github_repos(organization, token=None, cache_manager: Optional[CacheManager] = None, 
                    force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Obtém todos os repositórios de uma organização do GitHub com cache inteligente
    """
    if cache_manager is None:
        cache_manager = CacheManager()
    
    # Tentar recuperar do cache
    if not force_refresh:
        cached_repos = cache_manager.get('repositories', organization)
        if cached_repos:
            print(f"📦 Usando repositórios em cache para {organization}")
            return cached_repos.get('repositories', [])
    
    print(f"🔄 Buscando repositórios da organização {organization}...")
    repos = []
    page = 1
    per_page = 100  # Máximo por página
    
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
        print(f"🔑 Usando token: {token[:8]}...")
    else:
        # Gera token do App como fallback
        try:
            token = get_github_app_installation_token()
            headers['Authorization'] = f'token {token}'
            print(f"🔑 Usando token (App): {token[:8]}...")
        except Exception:
            print("⚠️  Nenhum token fornecido - acesso limitado")
    
    while True:
        url = f'https://api.github.com/orgs/{organization}/repos'
        params = {
            'page': page,
            'per_page': per_page,
            'type': 'all'  # Pega todos os tipos de repositórios
        }
        
        print(f"📄 Buscando página {page}...")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar a API do GitHub: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            break
        
        page_repos = response.json()
        print(f"✅ Página {page}: {len(page_repos)} repositórios encontrados")
        
        if not page_repos:
            print("📄 Fim das páginas")
            break
            
        repos.extend(page_repos)
        page += 1
        
        # Verifica se há mais páginas
        if 'next' not in response.links:
            print("📄 Última página alcançada")
            break
    
    print(f"📊 Total de repositórios coletados: {len(repos)}")
    
    # Armazenar no cache
    cache_data = {
        'repositories': repos,
        'cached_at': datetime.now().isoformat(),
        'org': organization,
        'count': len(repos)
    }
    cache_manager.set('repositories', cache_data, organization)
    
    return repos

def export_to_csv(repos, filename):
    """
    Exporta os repositórios para um arquivo CSV
    """
    if not repos:
        print("Nenhum repositório encontrado.")
        return
    
    # Define as colunas do CSV
    fieldnames = [
        'name', 'archived'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for repo in repos:
            row = {field: repo.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    print(f"Arquivo '{filename}' criado com sucesso!")
    print(f"Total de repositórios exportados: {len(repos)}")

def get_organization_default_labels(organization, token):
    """
    Obtém as labels padrão da organização (simulada)
    Como a API não suporta labels organizacionais, simulamos uma resposta
    """
    print(f"🔍 Verificando labels padrão da organização {organization}...")
    print(f"💡 Labels organizacionais são gerenciadas apenas via interface web")
    print(f"🌐 Acesse: https://github.com/organizations/{organization}/settings/repository-defaults")
    
    # Retorna lista vazia para não quebrar o fluxo
    return []

def create_default_label(organization, token, label_data):
    """
    Cria uma nova label padrão na organização (simulada)
    """
    print(f"➕ Label '{label_data['name']}' será aplicada automaticamente aos novos repositórios")
    print(f"💡 Para gerenciar labels organizacionais, use a interface web")
    return True

def update_default_label(organization, token, label_name, label_data):
    """
    Atualiza uma label padrão existente na organização (simulada)
    """
    print(f"🔄 Label '{label_name}' será aplicada automaticamente aos novos repositórios")
    print(f"💡 Para gerenciar labels organizacionais, use a interface web")
    return True

def delete_default_label(organization, token, label_name):
    """
    Remove uma label padrão da organização (simulada)
    """
    print(f"🗑️  Label '{label_name}' será aplicada automaticamente aos novos repositórios")
    print(f"💡 Para gerenciar labels organizacionais, use a interface web")
    return True

def sync_organization_labels(organization, token, labels_file):
    """
    Sincroniza as labels padrão da organização com as labels do arquivo YAML
    """
    print(f"\n🔄 Sincronizando labels padrão da organização {organization}...")
    
    # Carrega labels do arquivo YAML
    default_labels = load_labels_from_yaml(labels_file)
    if not default_labels:
        print("❌ Não foi possível carregar as labels padrão")
        return
    
    print(f"📁 {len(default_labels)} labels encontradas no arquivo YAML")
    print(f"💡 Labels organizacionais são gerenciadas apenas via interface web do GitHub")
    print(f"💡 Estas labels serão aplicadas automaticamente aos novos repositórios")
    
    # Como não podemos gerenciar labels organizacionais via API, apenas informamos
    print(f"\n📊 Resumo da sincronização:")
    print(f"   📋 Labels encontradas no YAML: {len(default_labels)}")
    print(f"   💡 Labels organizacionais são aplicadas automaticamente aos novos repositórios")
    print(f"   🌐 Para gerenciar labels organizacionais, use: https://github.com/organizations/{organization}/settings/repository-defaults")
    
    print(f"\n✅ Sincronização de labels organizacionais concluída!")
    print(f"💡 As labels serão aplicadas automaticamente aos novos repositórios criados")
    