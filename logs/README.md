# Logs do Sistema

Esta pasta contém os arquivos de log do sistema de gestão GitHub.

## Estrutura

```
logs/
├── README.md                    # Este arquivo
├── github_management.log        # Log principal do sistema
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

## Boas Práticas

1. **Não versionar**: Logs estão no `.gitignore`
2. **Rotação**: Limpar logs antigos periodicamente
3. **Monitoramento**: Usar `tail -f` para acompanhar execução
4. **Debug**: Verificar logs quando houver problemas

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
