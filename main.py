#!/usr/bin/env python3
"""
GitHub Organization Management Tool
"""
import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List
from scripts.repos_list import sync_organization_labels, get_github_repos, export_to_csv
from scripts.labels_sync import sync_repository_labels

DEFAULT_ORG = 'splor-mg'
DEFAULT_LABELS_FILE = 'docs/labels.yaml'

# Configuração de logging
def setup_logging(verbose: bool = False) -> None:
    """Configura o sistema de logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('github_management.log')
        ]
    )

def load_environment() -> dict:
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
    
    # Retorna configurações
    return {
        'github_token': os.getenv('GITHUB_TOKEN'),
        'github_org': os.getenv('GITHUB_ORG', DEFAULT_ORG),
        'labels_file': os.getenv('GITHUB_LABELS_FILE', DEFAULT_LABELS_FILE)
    }

def validate_config(config: dict) -> bool:
    """Valida se a configuração está correta"""
    if not config['github_token']:
        print("❌ GITHUB_TOKEN não encontrado!")
        print("💡 Configure a variável GITHUB_TOKEN no arquivo .env")
        return False
    
    print(f"🔧 Configurações:")
    print(f"   Organização: {config['github_org']}")
    print(f"   Arquivo de labels: {config['labels_file']}")
    print(f"   Token: {config['github_token'][:8]}...")
    
    return True



def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="GitHub Organization Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py --sync-org                    # Sincroniza labels da organização
  python main.py --list-repos                  # Lista repositórios
  python main.py --sync-repos                  # Sincroniza labels nos repositórios
  python main.py --all                         # Executa todas as operações
  python main.py --verbose                     # Modo verboso
  python main.py --sync-repos --no-delete-extras  # Sincroniza sem deletar labels extras
        """
    )
    
    # Argumentos
    parser.add_argument('--sync-org', action='store_true', 
                       help='Sincroniza labels padrão da organização')
    parser.add_argument('--list-repos', action='store_true',
                       help='Lista repositórios da organização')
    parser.add_argument('--sync-repos', action='store_true',
                       help='Sincroniza labels em todos os repositórios')
    parser.add_argument('--all', action='store_true',
                       help='Executa todas as operações')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Modo verboso com mais detalhes')
    parser.add_argument('--no-delete-extras', action='store_true',
                       help='Não deleta labels extras (apenas adiciona/atualiza)')
    
    args = parser.parse_args()
    
    # Se nenhum argumento foi fornecido, mostra ajuda
    if not any([args.sync_org, args.list_repos, args.sync_repos, args.all]):
        parser.print_help()
        return
    
    # Configura logging
    setup_logging(args.verbose)
    
    # Carrega configurações
    config = load_environment()
    
    # Valida configuração
    if not validate_config(config):
        sys.exit(1)
    
    print(f"\n🚀 Iniciando GitHub Organization Management Tool")
    print(f"{'='*60}")
    
    success = True
    
    try:
        # Executa operações baseado nos argumentos
        if args.all or args.sync_org:
            try:
                print(f"\n🔄 Sincronizando organização: {config['github_org']}")
                sync_organization_labels(
                    config['github_org'], 
                    config['github_token'], 
                    config['labels_file']
                )
                print("✅ Sincronização da organização concluída!")
            except Exception as e:
                print(f"❌ Erro na sincronização da organização: {e}")
                logging.error(f"Erro na sincronização da organização: {e}")
                success = False
        
        if args.all or args.list_repos:
            try:
                print(f"\n📊 Listando repositórios da organização: {config['github_org']}")
                repos = get_github_repos(config['github_org'], config['github_token'])
                
                if repos:
                    # Cria diretório docs se não existir
                    docs_dir = Path('docs')
                    docs_dir.mkdir(exist_ok=True)
                    
                    # Exporta para CSV
                    filename = docs_dir / 'repos_list.csv'
                    export_to_csv(repos, str(filename))
                    
                    # Mostra alguns exemplos
                    print(f"\n📋 Primeiros 5 repositórios encontrados:")
                    for repo in repos[:5]:
                        print(f"   - {repo['name']} ({repo.get('language', 'N/A')})")
                    
                    print(f"✅ Total de repositórios: {len(repos)}")
                else:
                    print("❌ Nenhum repositório encontrado")
                    success = False
            except Exception as e:
                print(f"❌ Erro ao listar repositórios: {e}")
                logging.error(f"Erro ao listar repositórios: {e}")
                success = False
        
        if args.all or args.sync_repos:
            try:
                print(f"\n🏷️  Sincronizando labels nos repositórios da organização: {config['github_org']}")
                
                # Informa sobre o comportamento de deleção
                if args.no_delete_extras:
                    print("⚠️  Modo conservador: labels extras NÃO serão removidas")
                else:
                    print("🗑️  Modo completo: labels extras serão removidas automaticamente (padrão)")
                
                repos = get_github_repos(config['github_org'], config['github_token'])
                
                if not repos:
                    print("❌ Nenhum repositório encontrado para sincronizar")
                    success = False
                else:
                    # Sincroniza labels em cada repositório
                    success_count = 0
                    for repo in repos:
                        if repo.get('archived', False):
                            print(f"⏭️  Pulando repositório arquivado: {repo['name']}")
                            continue
                            
                        try:
                            print(f"🔄 Sincronizando {repo['name']}...")
                            sync_repository_labels(
                                config['github_org'],
                                repo['name'],
                                config['github_token'],
                                config['labels_file'],
                                delete_extras=not args.no_delete_extras
                            )
                            success_count += 1
                        except Exception as e:
                            print(f"❌ Erro ao sincronizar {repo['name']}: {e}")
                            logging.error(f"Erro ao sincronizar {repo['name']}: {e}")
                    
                    print(f"✅ Sincronização concluída! {success_count}/{len(repos)} repositórios processados")
            except Exception as e:
                print(f"❌ Erro na sincronização dos repositórios: {e}")
                logging.error(f"Erro na sincronização dos repositórios: {e}")
                success = False
        
        # Resultado final
        print(f"\n{'='*60}")
        if success:
            print("🎉 Todas as operações foram concluídas com sucesso!")
        else:
            print("⚠️  Algumas operações falharam. Verifique os logs para mais detalhes.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Operação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        logging.error(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
