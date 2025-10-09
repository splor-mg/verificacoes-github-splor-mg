# Listagem de Repositórios

Este documento explica como funciona a listagem e exportação de repositórios da organização GitHub.

## Visão Geral

O script `repos_list.py` lista todos os repositórios de uma organização GitHub e exporta para arquivo CSV, fornecendo informações básicas para outros scripts do sistema.

## Arquivo: `scripts/repos_list.py`

### Função Principal

**Lista repositórios da organização e exporta para CSV.**

### O que faz:

1. **Consulta API REST** do GitHub
2. **Lista todos os repositórios** da organização
3. **Exporta para CSV** com informações básicas
4. **Suporte a paginação** (até 100 repositórios por página)

## Estrutura do CSV

### Arquivo: `config/repos_list.csv`
```csv
name,archived
verificacoes-github-splor-mg,False
atividades,False
volumes-loa,False
dados-sigplan-planejamento,False
```

### Campos Exportados
- **name**: Nome do repositório
- **archived**: Status de arquivamento (True/False)

## Uso

### Comando Básico
```bash
poetry run python main.py --repos-list
```

### Via Task
```bash
poetry run task repos-list
```

### Diretamente
```bash
poetry run python scripts/repos_list.py
```

## Configuração

### Variáveis de Ambiente
```bash
GITHUB_ORG=splor-mg                    # Organização padrão
GITHUB_APP_ID=123456                  # ID do GitHub App
GITHUB_APP_INSTALLATION_ID=789012    # ID da instalação
GITHUB_APP_PRIVATE_KEY="-----BEGIN..." # Chave privada
```

### Autenticação
- **GitHub App**: Usa `github_app_auth.py` para obter token
- **Fallback**: Tenta usar token fornecido como parâmetro
- **Público**: Se não houver token, acesso limitado

## Fluxo de Processamento

1. **Autenticação**: Gera token via GitHub App
2. **Consulta API**: Busca repositórios da organização
3. **Paginação**: Processa todas as páginas (100 por página)
4. **Filtragem**: Inclui todos os tipos de repositórios
5. **Exportação**: Salva em CSV com campos básicos
6. **Resumo**: Exibe estatísticas da listagem

## Exemplo de Saída

```
🔑 Usando token (App): ghs_OfuC...
📄 Buscando página 1...
✅ Página 1: 100 repositórios encontrados
📄 Buscando página 2...
✅ Página 2: 39 repositórios encontrados
📄 Última página alcançada
📊 Total de repositórios coletados: 139
Arquivo 'config/repos_list.csv' criado com sucesso!
Total de repositórios exportados: 139

📋 Primeiros 5 repositórios encontrados:
   - atividades (Python)
   - volumes-loa (TeX)
   - volumes-docker (TeX)
   - volumes-ppag (TeX)
   - dados-sigplan-planejamento (Python)
✅ Total de repositórios: 139
```

## Parâmetros da API

### URL da API
```
GET https://api.github.com/orgs/{organization}/repos
```

### Parâmetros
- **page**: Número da página (inicia em 1)
- **per_page**: Repositórios por página (máximo 100)
- **type**: Tipo de repositórios (all, public, private, forks, sources, member)

### Headers
```json
{
  "Accept": "application/vnd.github.v3+json",
  "Authorization": "token ghs_..."
}
```

## Integração com Outros Scripts

### Labels Sync
- Usa `config/repos_list.csv` para obter lista de repositórios
- Processa cada repositório para sincronizar labels

### Issues Close Date
- Usa `config/repos_list.csv` para obter repositórios
- Busca issues em cada repositório para processar

### Projects Panels
- Não usa diretamente, mas pode ser executado em sequência
- Mantém dados organizacionais atualizados

## Troubleshooting

### Erro: "Erro ao acessar a API do GitHub"
- Verifique se o token está válido
- Confirme se o App tem permissões adequadas
- Teste a autenticação com `github_app_auth.py`

### Erro: "Nenhum repositório encontrado"
- Verifique se a organização tem repositórios
- Confirme se o App tem acesso aos repositórios
- Teste com `--verbose` para mais detalhes

### Repositórios não listados
- Verifique se os repositórios não estão arquivados
- Confirme se o App tem permissão de leitura
- Teste com diferentes tipos de repositórios

## Limitações

### Rate Limits
- **GitHub API**: 5000 requests/hora para Apps
- **Paginação**: Máximo 100 repositórios por página
- **Timeout**: 30 segundos por requisição

### Tipos de Repositórios
- **Incluídos**: Todos os tipos (all)
- **Filtros**: Apenas por status de arquivamento
- **Ordenação**: Por data de criação (padrão GitHub)

## Otimizações

### Cache
- Arquivo CSV é regenerado a cada execução
- Não há cache de dados entre execuções
- Recomendado executar antes de outros scripts

### Performance
- Processamento sequencial por página
- Sem processamento paralelo
- Adequado para organizações com até 1000 repositórios
