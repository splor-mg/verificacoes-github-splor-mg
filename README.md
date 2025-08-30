
# Verificações GitHub SPLOR-MG

Scripts para extrair e sincronizar informações de organizações GitHub.

## Scripts Disponíveis

### 1. Listar Repositórios

```bash
poetry run python main.py --list-repos
```

Gera `docs/repos_list.csv` com todos os repositórios da organização.

### 2. Sincronizar Labels da Organização

```bash
poetry run python main.py --sync-org
```

Sincroniza labels padrão da organização baseado em `docs/labels.yaml`.

### 3. Sincronizar Labels nos Repositórios

```bash
poetry run python main.py --sync-repos
```

Sincroniza labels em todos os repositórios (cria, atualiza e **deleta labels extras**).

### 4. Executar Todas as Operações

```bash
poetry run python main.py --all
```

### 5. Modo Conservador (não deleta labels extras)

```bash
poetry run python main.py --sync-repos --no-delete-extras
```

## Configuração

1. **Criar arquivo `.env`** na raiz do projeto:

```bash
GITHUB_TOKEN=seu_token_aqui
GITHUB_ORG=nome_da_organizacao
```

2. **Gerar token GitHub** em: Settings → Developer settings → Personal access tokens
   - Escopo: `repo` (para acesso aos repositórios)
   - Escopo: `admin:org` (para gerenciar labels organizacionais)

3. **Secrets necessários:**
   - **Organização**: Para repositórios públicos com o nome GH_TOKEN
   - **Repositório**: Para repositórios privados com o nome GH_TOKEN

## ⚠️ Alerta Importante sobre Labels

**ATENÇÃO**: Se eventualmente alguém atualizar manualmente o nome de uma label existente (por exemplo, alterar de "bug" para "bugs") sem alterar as default-labels em 'docs/labels.yml', quando os scripts de sincronização de labels deste repositório rodarem, o nome da label  "bugs" retornará para "bug" e será **automaticamente removida de todos os issues** onde estava aplicada.

**O que acontece quando você altera:**

- **Nome da label**: A label é removida de todos os issues automaticamente
- **Descrição da label**: ✅ Não afeta os issues (mantém-se aplicada)
- **Cor da label**: ✅ Não afeta os issues (mantém-se aplicada)

**Recomendação**: Se precisar alterar o nome de uma label, considere:

1. Criar uma nova label com o nome desejado
2. Aplicar a nova label nos issues que tinham a label antiga
3. Remover a label antiga apenas após a migração
4. Atualizar o template `docs/labels.yaml` com o novo nome da label
5. Executar os protocolos de sincronização (`poetry run python main.py --sync-repos`)

## Instalação

### Pré-requisitos

- Python 3.11+
- Poetry

### Instalar dependências

```bash
poetry install
```

## Organização

- **`scripts/`**: Scripts Python para sincronização de labels e listagem de repositórios
  - `repos_list.py`: Lista repositórios da organização
  - `labels_sync.py`: Sincroniza labels entre repositórios
- **`docs/`**: Arquivos de configuração e dados
  - `labels.yaml`: Template de labels padrão
  - `repos_list.csv`: Lista de repositórios (gerado automaticamente)
- **`.github/workflows/`**: Workflows GitHub Actions para automação
  - `labels-sync.yml`: Sincronização automática de labels

## Uso via GitHub Actions

O projeto inclui um workflow que pode ser executado manualmente para sincronizar labels:

1. Vá para a aba "Actions"
2. Selecione "labels-sync"
3. Clique em "Run workflow"
4. Escolha a organização e execute
