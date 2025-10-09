# Guia de Configuração Inicial

Este guia explica como configurar o ambiente para usar o sistema de verificações GitHub.

## Pré-requisitos

- Python 3.11+
- Poetry
- Acesso à organização GitHub
- Permissões para criar GitHub App

## 1. Instalação

### Clone o repositório
```bash
git clone https://github.com/splor-mg/verificacoes-github-splor-mg.git
cd verificacoes-github-splor-mg
```

### Instale dependências
```bash
poetry install
```

## 2. Configuração do GitHub App

### Criar GitHub App

1. Vá para **Settings** da organização
2. Clique em **Developer settings** → **GitHub Apps**
3. Clique em **New GitHub App**
4. Configure:
   - **App name**: `verificacoes-github-splor-mg`
   - **Homepage URL**: URL do repositório
   - **Webhook**: Desabilitado
   - **Permissions**:
     - Repository permissions: **Contents** (Read), **Issues** (Write), **Metadata** (Read)
     - Organization permissions: **Members** (Read)
   - **Subscribe to events**: Issues, Repository

### Instalar GitHub App

1. Na página do App, clique em **Install App**
2. Selecione a organização
3. Configure permissões se necessário

### Obter Credenciais

1. **App ID**: Na página do App (Settings → General)
2. **Installation ID**: Na página de instalação
3. **Private Key**: Generate private key e baixe o arquivo

## 3. Configuração do Ambiente

### Criar arquivo .env
```bash
cp .env.example .env
```

### Configurar variáveis
```bash
# Organização
GITHUB_ORG=splor-mg

# GitHub App
GITHUB_APP_ID=123456
GITHUB_APP_INSTALLATION_ID=789012
GITHUB_APP_PRIVATE_KEY_PATH=/path/to/private-key.pem

# Projeto padrão (opcional)
GITHUB_PROJECT_PANEL_DEFAULT=13
```

## 4. Teste da Configuração

### Verificar autenticação
```bash
poetry run python main.py --repos-list
```

### Sincronizar labels
```bash
poetry run python main.py --sync-labels
```

### Atualizar projetos
```bash
poetry run python main.py --projects-panels-info
```

## 5. Configuração para GitHub Actions

### Secrets da Organização

Configure os seguintes secrets na organização:

- `GITHUB_APP_ID`: ID numérico do GitHub App
- `GITHUB_APP_INSTALLATION_ID`: ID da instalação
- `GITHUB_APP_PRIVATE_KEY`: Conteúdo da chave privada (formato PEM)

### Workflows

Os workflows estão em `.github/workflows/`:
- `labels-sync.yml`: Sincronização de labels
- `issues-close-date.yml`: Gestão de datas em issues

## 6. Estrutura de Arquivos

```
config/
├── labels.yaml              # Template de labels
├── projects-panels-info.yml       # Dados dos projetos
├── projects-panels-list.yml  # Lista de projetos
├── repos_list.csv           # Lista de repositórios
├── issues-types.yml          # Tipos de issues
└── status.yml               # Status dos projetos

docs/
├── README.md                # Índice da documentação
├── labels-sync.md           # Documentação de labels
├── issues-close-date.md     # Documentação de issues
├── guides/
│   ├── setup.md            # Este guia
│   └── advanced-usage.md  # Uso avançado
└── examples/
    └── workflows.md        # Exemplos de workflows
```

## Troubleshooting

### Erro de autenticação
- Verifique se o GitHub App está instalado
- Confirme se as credenciais estão corretas
- Teste com `--verbose` para mais detalhes

### Erro de permissões
- Verifique as permissões do GitHub App
- Confirme se o App tem acesso aos repositórios

### Arquivos não encontrados
- Execute `--projects-panels-info` para gerar arquivos
- Verifique se a pasta `config/` existe
