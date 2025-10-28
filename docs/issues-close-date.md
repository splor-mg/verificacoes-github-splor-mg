# Gestão de Datas em Issues

Este documento descreve como funciona a gestão automática de campos de data em issues dos projetos GitHub.

## Visão Geral

O sistema gerencia automaticamente o campo "Data Fim" (ou outro campo configurável) em issues baseado no status do issue e na data de fechamento.

## Regras de Negócio

### Status != "Done"
- **Campo deve estar vazio** (limpa se preenchido)

### Status == "Done" + Issue Fechado + Campo Vazio
- **Preenche com data de fechamento** do issue

### Status == "Done" + Campo Preenchido
- **Mantém como está** (não altera)

### Status == "Done" + Issue Não Fechado
- **Não preenche** o campo

## Uso

### Comando Básico
```bash
poetry run python main.py --issues-close-date
```

### Seleção Interativa de Projetos
```bash
poetry run python main.py --issues-close-date-panel
```

### Projetos Específicos
```bash
poetry run python main.py --issues-close-date --issues-close-date-panels "1,2,3"
```

### Campo Customizado
```bash
poetry run python main.py --issues-close-date --issues-close-date-field "Data Conclusão"
```

## Configuração

### Arquivos Necessários

- `config/repos_list.csv` - Lista de repositórios
- `config/projects-panels-info.yml` - Dados completos dos projetos
- `config/projects-panels-list.yml` - Lista de projetos

### Variáveis de Ambiente

```bash
GITHUB_ORG=splor-mg
GITHUB_PROJECT_PANEL_DEFAULT=13  # Projeto padrão
```

### Autenticação

Usa GitHub App para autenticação:
- `GITHUB_APP_ID`
- `GITHUB_APP_INSTALLATION_ID`
- `GITHUB_APP_PRIVATE_KEY`

## Fluxo de Processamento

1. **Carrega repositórios** do arquivo CSV
2. **Carrega projetos** do arquivo YAML
3. **Filtra projetos** com o campo especificado
4. **Para cada repositório**:
   - Busca issues via GraphQL (com filtro por `updatedAt` quando o filtro por data está ativo)
   - Para cada issue:
     - Verifica status no projeto
     - Aplica regras de negócio
     - Atualiza campo se necessário

## Exemplos de Uso

### Primeira Execução (Todos os Issues)
```bash
poetry run python main.py --issues-close-date --issues-all
```

### Últimos 30 Dias
```bash
poetry run python main.py --issues-close-date --issues-days 30
```

### Workflow Completo
```bash
poetry run python main.py --all --issues-days 30
```

## Troubleshooting

### Erro: "Campo não encontrado"
- Verifique se o projeto possui o campo especificado
- Confirme o nome exato do campo

### Erro: "Projeto não encontrado"
- Execute `--projects-panels-info` para atualizar dados
- Verifique se o projeto existe na organização

### Issues não processados
- Verifique se o issue está associado ao projeto
- Confirme se o repositório não está arquivado

## GitHub Actions

O sistema inclui workflows para automação:

- **Atualização de projetos**: Atualiza dados dos projetos
- **Gestão de issues**: Processa issues automaticamente
- **Configuração dinâmica**: Atualiza opções de projetos

### Execução Manual

1. Vá para "Actions" no GitHub
2. Selecione "issue-closed-sync"
3. Clique em "Run workflow"
4. Configure parâmetros e execute

## Filtro por Data

- `--issues-days N` (padrão 7): processa issues com `updatedAt >= now_utc - N dias`, isto é, nos últimos N dias.
- `--issues-all` ou `--issues-days 0`: processa todos os issues (filtro desativado).
- Observação: o campo do projeto continuará sendo preenchido com `closedAt` (quando aplicável), o filtro usa `updatedAt` apenas para reduzir o escopo de busca.
