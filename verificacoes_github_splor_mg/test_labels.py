#!/usr/bin/env python3
"""
Script de teste para o gerenciador de labels.
Executa testes básicos sem fazer alterações reais no GitHub.
"""

import os
import sys
from unittest.mock import Mock, patch
from .labels_manager import GitHubLabelsManager

def test_labels_manager_initialization():
    """Testa a inicialização do gerenciador de labels."""
    print("Testando inicialização...")
    
    # Mock das variáveis de ambiente
    with patch.dict(os.environ, {
        'GITHUB_TOKEN': 'test_token',
        'GITHUB_ORG': 'test_org'
    }):
        # Mock do PyGithub
        with patch('verificacoes_github_splor_mg.labels_manager.Github') as mock_github:
            mock_github_instance = Mock()
            mock_github.return_value = mock_github_instance
            
            mock_org = Mock()
            mock_github_instance.get_organization.return_value = mock_org
            
            try:
                manager = GitHubLabelsManager()
                print("  ✓ Inicialização bem-sucedida")
                return True
            except Exception as e:
                print(f"  ✗ Erro na inicialização: {e}")
                return False

def test_standard_labels():
    """Testa se as labels padrão estão definidas corretamente."""
    print("Testando labels padrão...")
    
    try:
        # Mock das variáveis de ambiente
        with patch.dict(os.environ, {
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_ORG': 'test_org'
        }):
            with patch('verificacoes_github_splor_mg.labels_manager.Github') as mock_github:
                mock_github_instance = Mock()
                mock_github.return_value = mock_github_instance
                
                mock_org = Mock()
                mock_github_instance.get_organization.return_value = mock_org
                
                manager = GitHubLabelsManager()
                labels = manager.get_standard_labels()
                
                # Verifica se há labels definidas
                if len(labels) > 0:
                    print(f"  ✓ {len(labels)} labels padrão definidas")
                    
                    # Verifica estrutura das labels
                    for name, config in labels.items():
                        if 'color' in config and 'description' in config:
                            print(f"    ✓ {name}: {config['color']} - {config['description']}")
                        else:
                            print(f"    ✗ {name}: estrutura inválida")
                            return False
                    
                    return True
                else:
                    print("  ✗ Nenhuma label padrão definida")
                    return False
                    
    except Exception as e:
        print(f"  ✗ Erro ao testar labels padrão: {e}")
        return False

def test_label_categories():
    """Testa se as categorias de labels estão presentes."""
    print("Testando categorias de labels...")
    
    try:
        with patch.dict(os.environ, {
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_ORG': 'test_org'
        }):
            with patch('verificacoes_github_splor_mg.labels_manager.Github') as mock_github:
                mock_github_instance = Mock()
                mock_github.return_value = mock_github_instance
                
                mock_org = Mock()
                mock_github_instance.get_organization.return_value = mock_org
                
                manager = GitHubLabelsManager()
                labels = manager.get_standard_labels()
                
                # Verifica se as labels esperadas estão presentes
                expected_labels = ['bug', 'new-feature', 'chore', 'documentation', 'question', 'wontfix', 'meeting']
                found_labels = list(labels.keys())
                
                missing_labels = set(expected_labels) - set(found_labels)
                
                if not missing_labels:
                    print(f"  ✓ Todas as labels esperadas encontradas: {', '.join(found_labels)}")
                    return True
                else:
                    print(f"  ✗ Labels faltando: {', '.join(missing_labels)}")
                    return False
                    
    except Exception as e:
        print(f"  ✗ Erro ao testar categorias: {e}")
        return False

def test_color_format():
    """Testa se as cores das labels estão no formato correto (hexadecimal)."""
    print("Testando formato das cores...")
    
    try:
        with patch.dict(os.environ, {
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_ORG': 'test_org'
        }):
            with patch('verificacoes_github_splor_mg.labels_manager.Github') as mock_github:
                mock_github_instance = Mock()
                mock_github.return_value = mock_github_instance
                
                mock_org = Mock()
                mock_github_instance.get_organization.return_value = mock_org
                
                manager = GitHubLabelsManager()
                labels = manager.get_standard_labels()
                
                invalid_colors = []
                
                for name, config in labels.items():
                    color = config['color']
                    # Verifica se é hexadecimal válido (6 caracteres, 0-9, a-f)
                    if not (len(color) == 6 and all(c in '0123456789abcdef' for c in color.lower())):
                        invalid_colors.append(f"{name}: {color}")
                
                if not invalid_colors:
                    print("  ✓ Todas as cores estão no formato hexadecimal válido")
                    return True
                else:
                    print(f"  ✗ Cores inválidas encontradas: {', '.join(invalid_colors)}")
                    return False
                    
    except Exception as e:
        print(f"  ✗ Erro ao testar cores: {e}")
        return False

def main():
    """Função principal dos testes."""
    print("=== Testes do Gerenciador de Labels ===\n")
    
    tests = [
        test_labels_manager_initialization,
        test_standard_labels,
        test_label_categories,
        test_color_format
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Resultado dos Testes ===")
    print(f"Passou: {passed}/{total}")
    
    if passed == total:
        print("🎉 Todos os testes passaram!")
        return 0
    else:
        print("❌ Alguns testes falharam.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
