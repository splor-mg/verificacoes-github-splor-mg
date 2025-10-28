# Exemplos de Workflows

Este documento apresenta exemplos práticos de workflows GitHub Actions para automação.

## Workflow Básico - Sincronização de Labels

```yaml
name: Sync Labels
on:
  workflow_dispatch:
    inputs:
      organization:
        description: 'Organization name'
        required: true
        default: 'splor-mg'
      delete_extras:
        description: 'Delete extra labels'
        type: boolean
        default: false

jobs:
  sync-labels:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Poetry
        uses: snok/install-poetry@v1

      - name: Install dependencies
        run: poetry install --no-interaction

      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.GITHUB_APP_ID }}
          private-key: ${{ secrets.GITHUB_APP_PRIVATE_KEY }}
          owner: ${{ inputs.organization }}

      - name: Sync labels
        run: |
          poetry run python main.py --sync-labels \
            --org "${{ inputs.organization }}" \
            ${{ inputs.delete_extras && '--delete-extras' || '' }}
        env:
          GITHUB_TOKEN: ${{ steps.app-token.outputs.token }}
```

## Workflow Completo - Gestão de Issues

```yaml
name: Manage Issues
on:
  schedule:
    - cron: '0 2 * * 1'  # Segunda-feira às 2h
  workflow_dispatch:
    inputs:
      organization:
        description: 'Organization name'
        required: true
        default: 'splor-mg'
      project_number:
        description: 'Project number'
        required: true
        default: '13'
      field_name:
        description: 'Date field name'
        required: true
        default: 'Data Fim'

jobs:
  manage-issues:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Poetry
        uses: snok/install-poetry@v1

      - name: Install dependencies
        run: poetry install --no-interaction

      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.GITHUB_APP_ID }}
          private-key: ${{ secrets.GITHUB_APP_PRIVATE_KEY }}
          owner: ${{ inputs.organization }}

      - name: Update projects data
        run: |
          poetry run python main.py --projects-panels-info --projects-panels-list
        env:
          GITHUB_TOKEN: ${{ steps.app-token.outputs.token }}
          GITHUB_ORG: ${{ inputs.organization }}

      - name: Manage issues
        run: |
          poetry run python main.py --issues-close-date \
            --issues-close-date-panels "${{ inputs.project_number }}" \
            --issues-close-date-field "${{ inputs.field_name }}" \
            --org "${{ inputs.organization }}"
        env:
          GITHUB_TOKEN: ${{ steps.app-token.outputs.token }}
          GITHUB_ORG: ${{ inputs.organization }}

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add config/
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "Update projects data [skip ci]"
            git push
          fi
```

## Workflow de Teste

```yaml
name: Test Workflow
on:
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Poetry
        uses: snok/install-poetry@v1

      - name: Install dependencies
        run: poetry install --no-interaction

      - name: Run tests
        run: |
          poetry run python -m pytest tests/
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Check formatting
        run: poetry run black --check .

      - name: Check linting
        run: poetry run flake8 .
```

## Workflow de Deploy

```yaml
name: Deploy
on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Poetry
        uses: snok/install-poetry@v1

      - name: Install dependencies
        run: poetry install --no-interaction

      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.GITHUB_APP_ID }}
          private-key: ${{ secrets.GITHUB_APP_PRIVATE_KEY }}
          owner: 'splor-mg'

      - name: Run full workflow
        run: |
          poetry run python main.py --all --projects-panels-info --issues-close-date
        env:
          GITHUB_TOKEN: ${{ steps.app-token.outputs.token }}
          GITHUB_ORG: 'splor-mg'

      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add config/ docs/
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "Auto-update: $(date)"
            git push
          fi
```

## Configuração de Secrets

### Secrets da Organização

Configure os seguintes secrets na organização:

- `GITHUB_APP_ID`: ID numérico do GitHub App
- `GITHUB_APP_INSTALLATION_ID`: ID da instalação do App
- `GITHUB_APP_PRIVATE_KEY`: Conteúdo da chave privada (formato PEM)

### Secrets do Repositório

Para workflows específicos do repositório:

- `GITHUB_TOKEN`: Token padrão (gerado automaticamente)
- `GITHUB_ORG`: Nome da organização (opcional)

## Exemplos de Uso

### Execução Manual

1. Vá para a aba "Actions"
2. Selecione o workflow desejado
3. Clique em "Run workflow"
4. Configure os parâmetros
5. Clique em "Run workflow"

### Agendamento

```yaml
on:
  schedule:
    - cron: '0 2 * * 1'  # Segunda-feira às 2h
    - cron: '0 2 * * 5'  # Sexta-feira às 2h
```

### Triggers

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
  schedule:
    - cron: '0 2 * * 1'
```

## Troubleshooting

### Erro de Permissões

```yaml
permissions:
  contents: read
  issues: write
  pull-requests: write
```

### Erro de Token

```yaml
- name: Generate token
  id: app-token
  uses: actions/create-github-app-token@v2
  with:
    app-id: ${{ secrets.GITHUB_APP_ID }}
    private-key: ${{ secrets.GITHUB_APP_PRIVATE_KEY }}
    owner: ${{ inputs.organization }}
```

### Debug

```yaml
- name: Debug
  run: |
    echo "Organization: ${{ inputs.organization }}"
    echo "Project: ${{ inputs.project_number }}"
    echo "Field: ${{ inputs.field_name }}"
```
