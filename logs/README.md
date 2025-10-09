# Logs e Cache do Sistema

Esta pasta contém os arquivos de log e cache do sistema de gestão GitHub.

## Estrutura

```
logs/
├── README.md                    # Este arquivo
├── github_management.log        # Log principal do sistema
├── cache/                       # Cache de dados (não versionado)
│   ├── repositories_*.json      # Cache de repositórios
│   ├── issues_*.json            # Cache de issues
│   └── projects_*.json          # Cache de projetos
└── archived/                    # Logs antigos (futuro)
```

## Arquivos de Log

### `github_management.log`
- **Propósito**: Log principal de todas as operações
- **Conteúdo**: Execução de scripts, erros, debug
- **Rotação**: Manual (quando necessário)

## Comandos Úteis

### Monitorar logs em tempo real
```bash
tail -f logs/github_management.log
```

### Filtrar erros
```bash
grep "ERROR" logs/github_management.log
```

### Ver últimas 50 linhas
```bash
tail -n 50 logs/github_management.log
```

### Limpar logs
```bash
rm -f logs/github_management.log
```

## Cache

### `cache/`
- **Propósito**: Cache inteligente para dados do GitHub
- **Conteúdo**: Repositórios, issues, projetos em cache
- **TTL**: Cache expira automaticamente (configurável)
- **Não versionado**: Está no `.gitignore`

### Gerenciar cache
```bash
# Ver estatísticas do cache
poetry run python main.py --cache-stats

# Forçar refresh do cache
poetry run python main.py --force-refresh

# Limpar cache
rm -rf logs/cache/*
```

## Boas Práticas

1. **Não versionar**: Logs e cache estão no `.gitignore`
2. **Rotação**: Limpar logs antigos periodicamente
3. **Monitoramento**: Usar `tail -f` para acompanhar execução
4. **Debug**: Verificar logs quando houver problemas
5. **Cache**: Deixar cache funcionar automaticamente (TTL configurado)
6. **Limpeza**: Limpar cache apenas quando necessário

## Estrutura Futura

```
logs/
├── github_management.log        # Log principal
├── labels_sync.log              # Log específico de labels
├── issues_close_date.log        # Log específico de issues
└── archived/                    # Logs antigos
    ├── github_management_2024-01-15.log
    └── github_management_2024-01-16.log
```
