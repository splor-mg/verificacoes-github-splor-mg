#!/usr/bin/env python3
"""
Script para gerenciar labels do GitHub de forma uniforme.
Permite definir, criar e atualizar labels em repositórios da organização.
"""

import os
import sys
from typing import Dict, List, Optional
from github import Github, Repository, Label
from dotenv import load_dotenv
import argparse
import json

# Carrega variáveis de ambiente
load_dotenv()

class GitHubLabelsManager:
    """Classe para gerenciar labels do GitHub de forma uniforme."""
    
    def __init__(self, token: Optional[str] = None, org_name: Optional[str] = None):
        """
        Inicializa o gerenciador de labels.
        
        Args:
            token: Token de acesso do GitHub (padrão: GITHUB_TOKEN do .env)
            org_name: Nome da organização (padrão: GITHUB_ORG do .env)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("Token do GitHub é obrigatório. Configure GITHUB_TOKEN no .env ou passe como parâmetro.")
        
        self.github = Github(self.token)
        self.org_name = org_name or os.getenv('GITHUB_ORG')
        if not self.org_name:
            raise ValueError("Nome da organização é obrigatório. Configure GITHUB_ORG no .env ou passe como parâmetro.")
        
        self.org = self.github.get_organization(self.org_name)
    
    def get_standard_labels(self) -> Dict[str, Dict]:
        """
        Retorna as labels padrão definidas para a organização.
        Baseado no arquivo labels.yaml da organização.
        
        Returns:
            Dicionário com as labels padrão e suas configurações
        """
        return {
            # Labels de tipo
            "bug": {
                "color": "d73a4a",
                "description": "Algo não está funcionando corretamente"
            },
            "new-feature": {
                "color": "7069a2",
                "description": "Nova funcionalidade ou melhoria planejada"
            },
            "chore": {
                "color": "1d29b0",
                "description": "Tarefas de manutenção e organização"
            },
            "documentation": {
                "color": "3449e3",
                "description": "Melhorias ou adições à documentação"
            },
            "question": {
                "color": "760d9d",
                "description": "Pergunta ou dúvida sobre o projeto"
            },
            
            # Labels de status
            "wontfix": {
                "color": "78e11f",
                "description": "Issue não será corrigida ou implementada"
            },
            
            # Labels de eventos/reuniões
            "meeting": {
                "color": "f1ffab",
                "description": "Relacionado a reuniões ou eventos"
            }
        }
    
    def apply_labels_to_repo(self, repo_name: str, labels: Optional[Dict[str, Dict]] = None) -> None:
        """
        Aplica as labels padrão a um repositório específico.
        
        Args:
            repo_name: Nome do repositório
            labels: Dicionário de labels (padrão: labels padrão da organização)
        """
        if labels is None:
            labels = self.get_standard_labels()
        
        try:
            repo = self.org.get_repo(repo_name)
            print(f"Aplicando labels ao repositório: {repo_name}")
            
            for label_name, label_config in labels.items():
                try:
                    # Verifica se a label já existe
                    existing_label = repo.get_label(label_name)
                    
                    # Atualiza a label existente se necessário
                    if (existing_label.color != label_config['color'] or 
                        existing_label.description != label_config['description']):
                        existing_label.edit(
                            name=label_name,
                            color=label_config['color'],
                            description=label_config['description']
                        )
                        print(f"  ✓ Atualizada: {label_name}")
                    else:
                        print(f"  - Já existe: {label_name}")
                        
                except Exception as e:
                    # Cria nova label se não existir
                    try:
                        repo.create_label(
                            name=label_name,
                            color=label_config['color'],
                            description=label_config['description']
                        )
                        print(f"  + Criada: {label_name}")
                    except Exception as create_error:
                        print(f"  ✗ Erro ao criar {label_name}: {create_error}")
                        
        except Exception as e:
            print(f"Erro ao acessar repositório {repo_name}: {e}")
    
    def apply_labels_to_all_repos(self, labels: Optional[Dict[str, Dict]] = None) -> None:
        """
        Aplica as labels padrão a todos os repositórios da organização.
        
        Args:
            labels: Dicionário de labels (padrão: labels padrão da organização)
        """
        if labels is None:
            labels = self.get_standard_labels()
        
        print(f"Aplicando labels a todos os repositórios da organização: {self.org_name}")
        
        for repo in self.org.get_repos():
            if not repo.archived:  # Pula repositórios arquivados
                print(f"\nProcessando: {repo.name}")
                self.apply_labels_to_repo(repo.name, labels)
    
    def list_repo_labels(self, repo_name: str) -> List[Label]:
        """
        Lista todas as labels de um repositório.
        
        Args:
            repo_name: Nome do repositório
            
        Returns:
            Lista de labels do repositório
        """
        try:
            repo = self.org.get_repo(repo_name)
            return list(repo.get_labels())
        except Exception as e:
            print(f"Erro ao listar labels do repositório {repo_name}: {e}")
            return []
    
    def export_labels_config(self, filename: str = "labels_config.json") -> None:
        """
        Exporta a configuração das labels padrão para um arquivo JSON.
        
        Args:
            filename: Nome do arquivo de saída
        """
        labels = self.get_standard_labels()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(labels, f, indent=2, ensure_ascii=False)
        print(f"Configuração das labels exportada para: {filename}")
    
    def import_labels_config(self, filename: str) -> Dict[str, Dict]:
        """
        Importa configuração de labels de um arquivo JSON.
        
        Args:
            filename: Nome do arquivo de configuração
            
        Returns:
            Dicionário com as labels importadas
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                labels = json.load(f)
            print(f"Configuração das labels importada de: {filename}")
            return labels
        except Exception as e:
            print(f"Erro ao importar configuração: {e}")
            return self.get_standard_labels()


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(description="Gerenciador de Labels do GitHub")
    parser.add_argument("--repo", help="Nome do repositório específico")
    parser.add_argument("--all-repos", action="store_true", help="Aplicar a todos os repositórios")
    parser.add_argument("--list", help="Listar labels de um repositório")
    parser.add_argument("--export", help="Exportar configuração das labels")
    parser.add_argument("--import", dest="import_file", help="Importar configuração das labels")
    parser.add_argument("--token", help="Token de acesso do GitHub")
    parser.add_argument("--org", help="Nome da organização")
    
    args = parser.parse_args()
    
    try:
        # Inicializa o gerenciador
        manager = GitHubLabelsManager(token=args.token, org_name=args.org)
        
        if args.export:
            manager.export_labels_config(args.export)
        elif args.import_file:
            labels = manager.import_labels_config(args.import_file)
            if args.repo:
                manager.apply_labels_to_repo(args.repo, labels)
            elif args.all_repos:
                manager.apply_labels_to_all_repos(labels)
            else:
                print("Use --repo ou --all-repos para aplicar as labels importadas")
        elif args.list:
            labels = manager.list_repo_labels(args.list)
            print(f"\nLabels do repositório {args.list}:")
            for label in labels:
                print(f"  {label.name} ({label.color}) - {label.description}")
        elif args.repo:
            manager.apply_labels_to_repo(args.repo)
        elif args.all_repos:
            manager.apply_labels_to_all_repos()
        else:
            print("Labels padrão da organização:")
            labels = manager.get_standard_labels()
            for name, config in labels.items():
                print(f"  {name} ({config['color']}) - {config['description']}")
            print("\nUse --help para ver as opções disponíveis")
            
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
