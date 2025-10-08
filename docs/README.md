# Documentação - Verificações GitHub SPLOR-MG

Este diretório contém a documentação detalhada do projeto.

## Índice da Documentação

### Funcionalidades Principais
- **[Sincronização de Labels](labels-sync.md)** - Documentação completa sobre sincronização de labels
- **[Gestão de Datas em Issues](issues-close-date.md)** - Documentação sobre conferência de data de fechamento

### Scripts Específicos
- **[Autenticação GitHub App](github-app-auth.md)** - Sistema de autenticação via GitHub App
- **[Gestão de Projetos](projects-panels.md)** - Extração de dados dos projetos GitHub
- **[Listagem de Repositórios](repos-list.md)** - Listagem e exportação de repositórios

### Guias
- **[Configuração Inicial](guides/setup.md)** - Como configurar o ambiente
- **[Uso Avançado](guides/advanced-usage.md)** - Funcionalidades avançadas

### Exemplos
- **[Workflows](examples/workflows.md)** - Exemplos de workflows GitHub Actions

## Estrutura do Projeto

```
docs/
├── README.md (este arquivo)
├── labels-sync.md
├── issues-close-date.md
├── guides/
│   ├── setup.md
│   └── advanced-usage.md
└── examples/
    └── workflows.md
```

## Configuração

Os arquivos de configuração estão na pasta `config/`:
- `config/labels.yaml` - Template de labels
- `config/projects-panels.yml` - Dados dos projetos
- `config/repos_list.csv` - Lista de repositórios
