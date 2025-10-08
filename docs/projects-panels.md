# Gestão de Projetos GitHub (Projects v2)

Este documento explica como funciona a extração e gestão de dados dos projetos GitHub.

## Visão Geral

O script `projects_panels.py` extrai informações completas dos projetos GitHub (Projects v2) de uma organização e exporta para arquivos YAML estruturados.

## Arquivo: `scripts/projects_panels.py`

### Função Principal

**Extrai dados dos projetos GitHub via GraphQL e gera arquivos de configuração.**

### O que faz:

1. **Consulta API GraphQL** do GitHub
2. **Extrai informações** de todos os projetos da organização
3. **Gera dois arquivos YAML**:
   - `config/projects-panels.yml` - Dados completos
   - `config/projects-panels-list.yml` - Lista simplificada

## Estrutura dos Dados

### Arquivo Completo (`config/projects-panels.yml`)
```yaml
org: splor-mg
projects:
  - name: "Gestão à Vista AID"
    number: 13
    id: "PVT_kwDOByfrJc4AmH_f"
    description: "Projeto de gestão"
    fields:
      - name: "Status"
        id: "status_field_id"
        dataType: "SINGLE_SELECT"
        options:
          - name: "Todo"
            description: "A fazer"
            color: "f9d0c4"
          - name: "Done"
            description: "Concluído"
            color: "d4c5f9"
      - name: "Data Fim"
        id: "date_field_id"
        dataType: "DATE"
```

### Arquivo de Lista (`config/projects-panels-list.yml`)
```yaml
org: splor-mg
projects:
  - number: 13
    name: "Gestão à Vista AID"
    id: "PVT_kwDOByfrJc4AmH_f"
  - number: 16
    name: "Gestão Gabinete SPLOR"
    id: "PVT_kwDOByfrJc4A_Psy"
```

## Tipos de Campos Suportados

### 1. **SINGLE_SELECT** - Seleção Única
```yaml
- name: "Status"
  dataType: "SINGLE_SELECT"
  options:
    - name: "Todo"
      color: "f9d0c4"
    - name: "In Progress"
      color: "fbca04"
    - name: "Done"
      color: "d4c5f9"
```

### 2. **DATE** - Campo de Data
```yaml
- name: "Data Fim"
  dataType: "DATE"
```

### 3. **TEXT** - Campo de Texto
```yaml
- name: "Descrição"
  dataType: "TEXT"
```

### 4. **ITERATION** - Campo de Iteração
```yaml
- name: "Sprint"
  dataType: "ITERATION"
  iterations:
    - id: "iteration_1"
      title: "Sprint 1"
      startDate: "2024-01-01"
      endDate: "2024-01-15"
```

### 5. **NUMBER** - Campo Numérico
```yaml
- name: "Prioridade"
  dataType: "NUMBER"
```

## Uso

### Comando Básico
```bash
poetry run python scripts/projects_panels.py
```

### Com Parâmetros
```bash
# Organização específica
poetry run python scripts/projects_panels.py --org "minha-org"

# Arquivos customizados
poetry run python scripts/projects_panels.py \
  --output "meus_projetos.yml" \
  --list-output "minha_lista.yml"

# Modo verboso
poetry run python scripts/projects_panels.py --verbose
```

### Via main.py
```bash
# Atualizar dados dos projetos
poetry run python main.py --projects-panels

# Atualizar lista de projetos
poetry run python main.py --projects-list

# Ambos
poetry run python main.py --projects-panels --projects-list
```

## Configuração

### Variáveis de Ambiente
```bash
GITHUB_ORG=splor-mg                    # Organização padrão
GITHUB_APP_ID=123456                  # ID do GitHub App
GITHUB_APP_INSTALLATION_ID=789012    # ID da instalação
GITHUB_APP_PRIVATE_KEY="-----BEGIN..." # Chave privada
```

### Priorização de Configuração
1. **Argumentos** da linha de comando (maior prioridade)
2. **Variáveis** de ambiente (prioridade média)
3. **Valores** padrão (menor prioridade)

## Fluxo de Processamento

1. **Autenticação**: Gera token via GitHub App
2. **Consulta GraphQL**: Busca projetos da organização
3. **Paginação**: Processa todos os projetos (até 100 por página)
4. **Formatação**: Converte dados para estrutura YAML
5. **Exportação**: Salva em arquivos YAML
6. **Resumo**: Exibe estatísticas da extração

## Exemplo de Saída

```
📊 Buscando projetos da organização 'splor-mg'...
✅ Encontrados 2 projetos
✅ YAML salvo em: config/projects-panels.yml
✅ YAML salvo em: config/projects-panels-list.yml

📋 Resumo da extração:
   Organização: splor-mg
   Total de projetos: 2
   Arquivo completo: config/projects-panels.yml
   Arquivo de lista: config/projects-panels-list.yml
   Total de campos: 8
   - Gestão à Vista AID (#13): 4 campos
   - Gestão Gabinete SPLOR (#16): 4 campos
```

## Troubleshooting

### Erro: "Nenhum projeto encontrado"
- Verifique se a organização tem projetos
- Confirme se o App tem permissões adequadas
- Teste com `--verbose` para mais detalhes

### Erro: "GraphQL errors"
- Verifique as permissões do GitHub App
- Confirme se o App está instalado na organização
- Teste a autenticação com `github_app_auth.py`

### Campos não extraídos
- Verifique se os campos existem nos projetos
- Confirme se o App tem permissão de leitura
- Execute com `--verbose` para ver detalhes

## Integração com Outros Scripts

### Issues Close Date
- Usa `config/projects-panels.yml` para obter IDs dos projetos
- Filtra projetos por campos específicos (ex: "Data Fim")

### Workflows GitHub Actions
- Atualiza dados antes de processar issues
- Mantém informações atualizadas dos projetos

### Labels Sync
- Não usa diretamente, mas pode ser executado em sequência
- Mantém dados organizacionais atualizados
