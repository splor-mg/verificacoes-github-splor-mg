
# Verificações GitHub SPLOR-MG

Automatiza a gestão de organizações GitHub: inventaria repositórios, sincroniza labels conforme `config/labels.yaml`, atualiza dados de Projects (v2) e gerencia campos de data em issues — tudo autenticado via GitHub App e API GraphQL.

## Scripts Disponíveis

### 1. Listar Repositórios

```bash
poetry run python main.py --repos-list
# ou
poetry run task repos-list
```

Gera `config/repos_list.csv` com todos os repositórios da organização.

### 2. Painéis de Projetos - Listagem e Informações

```bash
poetry run python main.py --projects-panels-list
# ou
poetry run task projects-panels-list
```

Extrai dados completos dos projetos GitHub (Projects v2) e gera `config/projects-panels-info.yml` e `config/projects-panels-list.yml`.

### 3. Sincronizar Labels nos Repositórios

```bash
poetry run python main.py --sync-labels
# ou
poetry run task sync-labels

# remove labels extras (modo completo)
poetry run python main.py --sync-labels --delete-extras
# ou
poetry run task sync-labels-delete-extras
```

Por padrão, a sincronização é aditiva: garante que todos os repositórios tenham as labels definidas em `config/labels.yaml` (criando/atualizando quando necessário) sem remover labels extras; a exclusão só ocorre com `--delete-extras`.


**⚠️ Alerta Importante sobre Labels**

**ATENÇÃO**: Se eventualmente alguém atualizar manualmente o nome de uma label existente (por exemplo, alterar de "bug" para "bugs") sem alterar as default-labels em 'config/labels.yaml e os scripts de sincronização de labels deste repositório rodarem com o parâmetro "--delete-extras", a label  "bugs" será **removida de todos os issues** onde estava aplicada, e uma nova label "bug" criarda.


**Recomendação**: Se precisar alterar o nome de uma label, considere:

1. Criar uma nova label com o nome desejado
2. Aplicar a nova label nos issues que tinham a label antiga
3. Remover a label antiga apenas após a migração
4. Atualizar o template `config/labels.yaml` com o novo nome da label
5. Executar os protocolos de sincronização (`poetry run python main.py --sync-labels`)


### 4. Verificar/Preencher `Data Fim` nos Issues Fechados

```bash
poetry run python main.py --issues-close-date
# ou
poetry run task issues-close-date
```

Gerencia automaticamente o campo "Data Fim" em issues baseado no status e data de fechamento dos isses dos últimos 7 dias. 

### 5. Executar Todas as Operações

```bash
poetry run python main.py --all
# ou
poetry run task all
```

## Configuração

1. **Criar arquivo `.env`** na raiz do projeto (GitHub App):

```bash
cp .env.example .env
```

2. **Configuração de autenticação**

A autenticação é feita via **GitHub App** (nome: `verificacoes-github-splor-mg`). O sistema gera um JWT assinado com a chave privada do App e o troca por um token de instalação temporário, eliminando a necessidade de PATs. Para GitHub Actions, configure os seguintes secrets:

- `GITHUB_APP_ID`: ID numérico do GitHub App
- `GITHUB_APP_INSTALLATION_ID`: ID da instalação do App na organização  
- `GITHUB_APP_PRIVATE_KEY`: Chave privada do App (formato PEM)


## Instalação

### Pré-requisitos

- Python 3.11+
- Poetry

### Instalar dependências

```bash
poetry install
```


