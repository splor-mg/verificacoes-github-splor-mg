#!/usr/bin/env python3
"""
Script para converter arquivo YAML de labels para formato JSON.
Permite usar o arquivo labels.yaml com o gerenciador de labels.
"""

import yaml
import json
import sys
import os
from pathlib import Path

def yaml_to_labels_dict(yaml_file: str) -> dict:
    """
    Converte arquivo YAML para dicionário de labels no formato esperado.
    
    Args:
        yaml_file: Caminho para o arquivo YAML
        
    Returns:
        Dicionário com as labels no formato {name: {color, description}}
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
                    'description': label.get('description', ''),
                    'category': label.get('category', 'general')
                }
        
        return labels_dict
        
    except Exception as e:
        print(f"Erro ao ler arquivo YAML: {e}")
        return {}

def save_labels_json(labels_dict: dict, output_file: str) -> bool:
    """
    Salva o dicionário de labels em formato JSON.
    
    Args:
        labels_dict: Dicionário com as labels
        output_file: Caminho para o arquivo de saída
        
    Returns:
        True se salvou com sucesso, False caso contrário
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(labels_dict, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar arquivo JSON: {e}")
        return False

def print_labels_summary(labels_dict: dict) -> None:
    """
    Imprime um resumo das labels carregadas.
    
    Args:
        labels_dict: Dicionário com as labels
    """
    print(f"\n📋 Resumo das Labels ({len(labels_dict)} encontradas):")
    print("=" * 60)
    
    categories = {}
    for name, config in labels_dict.items():
        category = config.get('category', 'general')
        if category not in categories:
            categories[category] = []
        categories[category].append(name)
    
    for category, labels in categories.items():
        print(f"\n🏷️  {category.upper()}:")
        for label_name in labels:
            config = labels_dict[label_name]
            print(f"  • {label_name} ({config['color']}) - {config['description']}")

def main():
    """Função principal do script."""
    if len(sys.argv) < 2:
        print("Uso: python yaml_to_labels.py <arquivo_yaml> [arquivo_json_saida]")
        print("Exemplo: python yaml_to_labels.py labels.yaml labels_config.json")
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "labels_config.json"
    
    # Verifica se o arquivo YAML existe
    if not os.path.exists(yaml_file):
        print(f"❌ Arquivo YAML não encontrado: {yaml_file}")
        sys.exit(1)
    
    print(f"🔄 Convertendo {yaml_file} para {output_file}...")
    
    # Converte YAML para dicionário
    labels_dict = yaml_to_labels_dict(yaml_file)
    
    if not labels_dict:
        print("❌ Nenhuma label foi carregada do arquivo YAML")
        sys.exit(1)
    
    # Salva em JSON
    if save_labels_json(labels_dict, output_file):
        print(f"✅ Labels salvas em: {output_file}")
        print_labels_summary(labels_dict)
        
        print(f"\n💡 Para usar com o gerenciador de labels:")
        print(f"   python -m verificacoes_github_splor_mg.labels_manager --import {output_file} --all-repos")
    else:
        print("❌ Erro ao salvar arquivo JSON")
        sys.exit(1)

if __name__ == "__main__":
    main()
