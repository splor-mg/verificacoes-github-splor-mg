# Uso Avançado

Este guia apresenta funcionalidades avançadas e casos de uso específicos.

## Comandos Combinados

### Workflow Completo
```bash
# Executa tudo: labels, repositórios, projetos e issues
poetry run python main.py --all --projects-panels --issues-close-date
```

### Atualização Completa
```bash
# Atualiza projetos e processa TODOS os issues
poetry run python main.py --projects-panels --issues-close-date --issues-all
```

### Processamento por Período
```bash
# Últimos 30 dias
poetry run python main.py --issues-close-date --issues-days 30

# Últimos 90 dias
poetry run python main.py --issues-close-date --issues-days 90
```

## Configurações Avançadas

### Campos Customizados

```bash
# Usar campo "Data Conclusão" em vez de "Data Fim"
poetry run python main.py --issues-close-date --issues-field "Data Conclusão"
```

### Arquivos Customizados

```bash
# Usar arquivo de repositórios específico
poetry run python main.py --issues-close-date --issues-repos-file "meus_repos.csv"

# Usar arquivo de projetos específico
poetry run python main.py --issues-close-date --issues-projects-list "meus_projetos.yml"
```

### Organização Diferente

```bash
# Processar organização específica
poetry run python main.py --org "minha-org" --sync-labels
```

## Tasks do Poetry

### Lista de Tasks Disponíveis

```bash
# Ver todas as tasks
poetry run task --list
```

### Tasks Principais

```bash
# Labels
poetry run task sync-labels                    # Sincronização conservadora
poetry run task sync-labels-delete-extras      # Sincronização completa

# Projetos
poetry run task projects-panels                # Atualizar dados dos projetos
poetry run task projects-list                  # Atualizar lista de projetos

# Issues
poetry run task issues-close-date              # Gestão de datas (7 dias)
poetry run task issues-close-date-days-30      # Últimos 30 dias
poetry run task issues-close-date-all          # Todos os issues

# Combinadas
poetry run task projects-and-issues            # Projetos + Issues
poetry run task projects-and-issues-all        # Projetos + Todos os issues
poetry run task full-workflow                  # Workflow completo
```

## Modo Verboso

### Ativar logs detalhados
```bash
poetry run python main.py --verbose --sync-labels
```

### Logs em arquivo
```bash
# Logs são salvos em logs/github_management.log
poetry run python main.py --verbose --sync-labels
tail -f logs/github_management.log
```

## Casos de Uso Específicos

### Migração de Labels

1. **Backup das labels atuais**
```bash
# Exportar labels existentes
poetry run python main.py --list-repos
```

2. **Atualizar template**
```bash
# Editar config/labels.yaml
vim config/labels.yaml
```

3. **Sincronizar gradualmente**
```bash
# Testar em repositórios específicos
poetry run python main.py --sync-labels --repos "repo1,repo2"

# Sincronizar todos
poetry run python main.py --sync-labels
```

### Limpeza de Labels

```bash
# Remover labels extras (CUIDADO!)
poetry run python main.py --sync-labels --delete-extras
```

### Atualização de Projetos

```bash
# Atualizar dados dos projetos
poetry run python main.py --projects-panels --projects-list

# Atualizar workflow options
poetry run python scripts/update_workflow_options.py
```

## GitHub Actions

### Execução Manual

1. **Labels Sync**
   - Vá para Actions → "labels-sync"
   - Clique em "Run workflow"
   - Selecione organização e execute

2. **Issues Close Date**
   - Vá para Actions → "issue-closed-sync"
   - Clique em "Run workflow"
   - Configure parâmetros e execute

### Configuração Automática

```yaml
# .github/workflows/auto-sync.yml
name: Auto Sync
on:
  schedule:
    - cron: '0 2 * * 1'  # Segunda-feira às 2h
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run sync
        run: |
          poetry install
          poetry run python main.py --all
```

## Troubleshooting Avançado

### Debug de GraphQL

```bash
# Ativar logs detalhados
poetry run python main.py --verbose --issues-close-date
```

### Verificar Permissões

```bash
# Testar autenticação
poetry run python -c "
from scripts.github_app_auth import get_github_app_installation_token
token = get_github_app_installation_token()
print(f'Token: {token[:8]}...')
"
```

### Limpar Cache

```bash
# Remover arquivos temporários
rm -f logs/github_management.log
rm -f config/repos_list.csv
```

### Reset Completo

```bash
# Regenerar todos os arquivos
poetry run python main.py --all --projects-panels --issues-close-date
```
