#!/usr/bin/env python3
"""
Script de exemplo para configuração personalizada de labels.
Modifique este arquivo para definir suas próprias labels padrão.
"""

from labels_manager import GitHubLabelsManager

def get_custom_labels():
    """
    Define labels personalizadas para a organização.
    Baseado no arquivo labels.yaml da organização.
    
    Returns:
        Dicionário com as labels personalizadas
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

def main():
    """Função principal para aplicar labels personalizadas."""
    try:
        # Inicializa o gerenciador
        manager = GitHubLabelsManager()
        
        # Obtém as labels personalizadas
        custom_labels = get_custom_labels()
        
        print("Labels personalizadas definidas:")
        for name, config in custom_labels.items():
            print(f"  {name} ({config['color']}) - {config['description']}")
        
        # Pergunta ao usuário se quer aplicar
        response = input("\nDeseja aplicar essas labels? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            # Pergunta se quer aplicar a todos os repositórios ou um específico
            scope = input("Aplicar a todos os repositórios? (y/N): ").strip().lower()
            
            if scope in ['y', 'yes']:
                manager.apply_labels_to_all_repos(custom_labels)
            else:
                repo_name = input("Nome do repositório: ").strip()
                if repo_name:
                    manager.apply_labels_to_repo(repo_name, custom_labels)
                else:
                    print("Nome do repositório não fornecido.")
        else:
            print("Operação cancelada.")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
