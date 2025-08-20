#!/usr/bin/env python3
"""
Script para sincronizar labels do arquivo labels.yaml diretamente com o GitHub.
Este script lê o arquivo YAML e aplica as labels aos repositórios.
"""

import yaml
import os
import sys
from pathlib import Path
from labels_manager import GitHubLabelsManager

def load_labels_from_yaml(yaml_file: str) -> dict:
    """
    Carrega as labels do arquivo YAML.
    
    Args:
        yaml_file: Caminho para o arquivo YAML
        
    Returns:
        Dicionário com as labels no formato esperado
    """
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'labels' not in data:
            raise ValueError("Arquivo YAML deve conter uma chave 'labels'")
        
        labels_dict = {}
        
        for label in data['labels']:
            if 'name' in label and 'color' in label:
                labels_dict[label['name']] = {
                    'color': label['color'],
                    'description': label.get('description', '')
                }
        
        return labels_dict
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo YAML: {e}")
        return {}

def print_labels_summary(labels_dict: dict) -> None:
    """
    Imprime um resumo das labels carregadas.
    
    Args:
        labels_dict: Dicionário com as labels
    """
    print(f"\n📋 Labels carregadas do YAML ({len(labels_dict)} encontradas):")
    print("=" * 60)
    
    for name, config in labels_dict.items():
        print(f"  • {name} ({config['color']}) - {config['description']}")

def main():
    """Função principal do script."""
    yaml_file = "labels.yaml"
    
    # Verifica se o arquivo YAML existe
    if not os.path.exists(yaml_file):
        print(f"❌ Arquivo {yaml_file} não encontrado!")
        print("Certifique-se de que o arquivo está na raiz do projeto.")
        sys.exit(1)
    
    print(f"🔄 Carregando labels do arquivo {yaml_file}...")
    
    # Carrega as labels do YAML
    labels_dict = load_labels_from_yaml(yaml_file)
    
    if not labels_dict:
        print("❌ Nenhuma label foi carregada do arquivo YAML")
        sys.exit(1)
    
    print_labels_summary(labels_dict)
    
    # Pergunta ao usuário se quer aplicar
    print(f"\n💡 O que você gostaria de fazer?")
    print("1. Aplicar a um repositório específico")
    print("2. Aplicar a todos os repositórios")
    print("3. Apenas visualizar (não aplicar)")
    
    choice = input("\nEscolha uma opção (1-3): ").strip()
    
    if choice == "3":
        print("✅ Operação cancelada. Labels apenas visualizadas.")
        return
    
    try:
        # Inicializa o gerenciador
        manager = GitHubLabelsManager()
        
        if choice == "1":
            repo_name = input("Nome do repositório: ").strip()
            if repo_name:
                print(f"\n🚀 Aplicando labels ao repositório: {repo_name}")
                manager.apply_labels_to_repo(repo_name, labels_dict)
            else:
                print("❌ Nome do repositório não fornecido.")
                
        elif choice == "2":
            confirm = input("⚠️  Tem certeza que quer aplicar a TODOS os repositórios? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                print(f"\n🚀 Aplicando labels a todos os repositórios...")
                manager.apply_labels_to_all_repos(labels_dict)
            else:
                print("✅ Operação cancelada.")
                
        else:
            print("❌ Opção inválida.")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\n💡 Verifique se:")
        print("  • O arquivo .env está configurado corretamente")
        print("  • O GITHUB_TOKEN tem as permissões necessárias")
        print("  • O GITHUB_ORG está correto")

if __name__ == "__main__":
    main()
