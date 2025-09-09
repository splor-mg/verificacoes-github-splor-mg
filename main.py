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
from scripts.labels_sync import sync_labels_for_repo
from scripts.projects_panels import main as projects_panels_main
from scripts.issues_close_date import main as issues_close_date_main

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


def run_projects_panels(org: str, verbose: bool = False) -> bool:
    """Executa o script projects_panels.py"""
    try:
        print(f"\n📊 Atualizando dados dos projetos da organização: {org}")
        
        # Simular argumentos para o script projects_panels.py
        import sys
        original_argv = sys.argv.copy()
        
        # Configurar argumentos para projects_panels.py
        sys.argv = ['projects_panels.py', '--org', org]
        if verbose:
            sys.argv.append('--verbose')
        
        # Executar o script
        projects_panels_main()
        
        # Restaurar argumentos originais
        sys.argv = original_argv
        
        print("✅ Dados dos projetos atualizados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar dados dos projetos: {e}")
        logging.error(f"Erro ao atualizar dados dos projetos: {e}")
        return False


def run_issues_close_date(org: str, panel: bool = False, projects: str = None, 
                         field: str = 'Data Fim', verbose: bool = False) -> bool:
    """Executa o script issues_close_date.py"""
    try:
        print(f"\n🔧 Gerenciando campo '{field}' em projetos da organização: {org}")
        
        # Simular argumentos para o script issues_close_date.py
        import sys
        original_argv = sys.argv.copy()
        
        # Configurar argumentos para issues_close_date.py
        sys.argv = ['issues_close_date.py', '--org', org, '--field', field]
        
        if panel:
            sys.argv.append('--panel')
        elif projects:
            sys.argv.extend(['--projects', projects])
        
        if verbose:
            sys.argv.append('--verbose')
        
        # Executar o script
        issues_close_date_main()
        
        # Restaurar argumentos originais
        sys.argv = original_argv
        
        print("✅ Gerenciamento de issues concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerenciar issues: {e}")
        logging.error(f"Erro ao gerenciar issues: {e}")
        return False


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="GitHub Organization Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Labels e repositórios
  python main.py --sync-org                    # Sincroniza labels da organização
  python main.py --list-repos                  # Lista repositórios
  python main.py --sync-repos                  # Sincroniza labels nos repositórios
  python main.py --all                         # Executa todas as operações
  python main.py --verbose                     # Modo verboso
  python main.py --sync-repos --delete-extras  # Sincroniza e remove labels extras
  python main.py --org minha-org --repos repo1,repo2  # Sincroniza organização e repositórios específicos
  python main.py --labels /caminho/labels.yaml  # Usa arquivo de labels customizado
  
  # Projetos GitHub
  python main.py --projects-panels             # Atualiza dados dos projetos (projects-panels.yml)
  python main.py --projects-list               # Atualiza lista de projetos (projects-panels-list.yml)
  
  # Issues e campos de data
  python main.py --issues-close-date           # Gerencia campo Data Fim em projetos
  python main.py --issues-panel                # Seleção interativa de projetos para issues
  python main.py --issues-projects "1,2,3"     # Projetos específicos para issues
  python main.py --issues-field "Data Conclusão"  # Campo customizado para issues
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
    parser.add_argument('--delete-extras', action='store_true',
                       help='Deleta labels extras para manter 100% sincronizado')
    parser.add_argument('--org', type=str, help='Organização específica para sincronizar')
    parser.add_argument('--repos', type=str, help='Repositórios específicos (CSV ou lista separada por vírgula)')
    parser.add_argument('--labels', type=str, help='Arquivo de labels customizado')
    
    # Argumentos para projetos
    parser.add_argument('--projects-panels', action='store_true', 
                       help='Atualiza dados dos projetos GitHub (projects-panels.yml)')
    parser.add_argument('--projects-list', action='store_true',
                       help='Atualiza lista de projetos (projects-panels-list.yml)')
    
    # Argumentos para issues
    parser.add_argument('--issues-close-date', action='store_true',
                       help='Gerencia campo Data Fim em projetos GitHub')
    parser.add_argument('--issues-panel', action='store_true',
                       help='Seleção interativa de projetos para issues')
    parser.add_argument('--issues-projects', type=str,
                       help='Projetos específicos para issues (números separados por vírgula)')
    parser.add_argument('--issues-field', type=str, default='Data Fim',
                       help='Nome do campo de data para issues (padrão: Data Fim)')
    
    args = parser.parse_args()
    
    # Se nenhum argumento foi fornecido, mostra ajuda
    if not any([args.sync_org, args.list_repos, args.sync_repos, args.all, 
                args.projects_panels, args.projects_list, args.issues_close_date, args.issues_panel]):
        parser.print_help()
        return
    
    # Configura logging
    setup_logging(args.verbose)
    
    # Carrega configurações
    config = load_environment()
    
    # Aplica argumentos da linha de comando (maior prioridade)
    if args.org:
        config['github_org'] = args.org
    if args.labels:
        config['labels_file'] = args.labels
    
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
                
                # Carregar labels do arquivo YAML
                from scripts.labels_sync import load_labels_from_yaml
                labels = load_labels_from_yaml(config['labels_file'])
                if not labels:
                    print("❌ Não foi possível carregar as labels")
                    success = False
                    return
                
                # Informa sobre o comportamento de deleção
                if args.delete_extras:
                    print("🗑️  Modo completo: labels extras serão removidas automaticamente")
                else:
                    print("⚠️  Modo conservador: labels extras NÃO serão removidas (padrão)")
                
                # Carrega repositórios (específicos ou todos)
                if args.repos:
                    from scripts.labels_sync import load_repos
                    repos = load_repos(args.repos, config['github_org'])
                    if not repos:
                        print("❌ Nenhum repositório encontrado na lista especificada")
                        success = False
                        return
                    print(f"🎯 Sincronizando {len(repos)} repositórios específicos")
                else:
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
                            sync_labels_for_repo(
                                repo['name'],
                                labels,
                                config['github_token'],
                                config['github_org'],
                                delete_extras=args.delete_extras
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
        
        # Executar comandos de projetos
        if args.all or args.projects_panels or args.projects_list:
            try:
                if not run_projects_panels(config['github_org'], args.verbose):
                    success = False
            except Exception as e:
                print(f"❌ Erro ao executar projects_panels: {e}")
                logging.error(f"Erro ao executar projects_panels: {e}")
                success = False
        
        # Executar comandos de issues
        if args.all or args.issues_close_date or args.issues_panel:
            try:
                # Só usar modo interativo se explicitamente solicitado
                panel_mode = args.issues_panel
                if not run_issues_close_date(
                    config['github_org'], 
                    panel=panel_mode,
                    projects=args.issues_projects,
                    field=args.issues_field,
                    verbose=args.verbose
                ):
                    success = False
            except Exception as e:
                print(f"❌ Erro ao executar issues_close_date: {e}")
                logging.error(f"Erro ao executar issues_close_date: {e}")
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
