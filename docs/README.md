# GitHub Organization Management Tool - SPLOR-MG

Ferramenta completa para gerenciamento de organizações GitHub, incluindo sincronização de labels, gestão de projetos e controle de datas em issues.

## 🚀 Início Rápido

```bash
# Instalar dependências
poetry install

# Executar todas as operações
poetry run task all

# Ver todas as tasks disponíveis
poetry run task --help
```

## 📋 Comandos Principais

### Comandos Python Diretos

```bash
# Listagem de repositórios
python main.py --repos-list

# Sincronização de labels
python main.py --sync-labels
python main.py --sync-labels --delete-extras  # Remove labels extras

# Gestão de projetos
python main.py --projects-panels-info         # Dados completos
python main.py --projects-panels-list         # Lista de projetos
python main.py --projects-panels-update       # Ambos

# Gestão de issues
python main.py --issues-close-date            # Últimos 7 dias (padrão)
python main.py --issues-close-date --issues-days 30  # Últimos 30 dias
python main.py --issues-close-date --issues-all     # Todos os issues

# Executar tudo
python main.py --all
```

### Tasks do Poetry (Recomendado)

```bash
# Tasks principais
poetry run task all                    # Executa tudo
poetry run task repos-list            # Lista repositórios
poetry run task sync-labels           # Sincroniza labels
poetry run task projects-panels-info  # Dados completos dos projetos
poetry run task projects-panels-list  # Lista de projetos
poetry run task issues-close-date     # Issues (últimos 7 dias)

# Tasks de personalização
poetry run task sync-labels-delete-extras     # Labels + remoção de extras
poetry run task issues-close-date-all         # Todos os issues
poetry run task issues-close-date-days 30     # Issues dos últimos 30 dias
poetry run task issues-close-date-panel       # Seleção interativa
```

## 🔧 Argumentos Comuns

### Filtros de Data (Issues)
- `--issues-days N` - Processa issues dos últimos N dias (padrão: 7)
- `--issues-all` - Processa todos os issues (sem filtro)

### Organização e Repositórios
- `--org ORG` - Organização específica
- `--repos "repo1,repo2"` - Repositórios específicos
- `--labels /caminho/labels.yaml` - Arquivo de labels customizado

### Modo Verboso
- `--verbose` ou `-v` - Logs detalhados

## 📁 Arquivos de Configuração

```
config/
├── labels.yaml                    # Template de labels
├── projects-panels-info.yml      # Dados completos dos projetos
├── projects-panels-list.yml      # Lista de projetos
└── repos_list.csv               # Lista de repositórios
```

## 🔐 Autenticação

Configure no arquivo `.env`:

```bash
GITHUB_ORG=splor-mg
GITHUB_APP_ID=seu_app_id
GITHUB_APP_INSTALLATION_ID=seu_installation_id
GITHUB_APP_PRIVATE_KEY_PATH=caminho/para/private_key.pem
```

## 📚 Documentação Detalhada

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

## 🎯 Casos de Uso Comuns

### Primeira Execução
```bash
# 1. Listar repositórios
poetry run task repos-list

# 2. Atualizar dados dos projetos
poetry run task projects-panels-update

# 3. Sincronizar labels
poetry run task sync-labels

# 4. Processar todos os issues (primeira vez)
poetry run task issues-close-date-all
```

### Execução Diária
```bash
# Processar apenas issues dos últimos 7 dias
poetry run task all
```

### Limpeza de Labels
```bash
# Sincronizar e remover labels extras
poetry run task sync-labels-delete-extras
```

## 🔄 GitHub Actions

O projeto inclui workflows automatizados:
- **Labels Sync** - Sincronização automática de labels
- **Issues Close Date** - Gestão automática de datas em issues
- **Projects Update** - Atualização automática de dados dos projetos

## 🛠️ Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
poetry install --with dev

# Executar testes
poetry run task test

# Formatar código
poetry run task format

# Verificar código
poetry run task check-all
```
