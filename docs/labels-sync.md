# Sincronização de Labels

Este documento descreve como funciona a sincronização de labels nos repositórios da organização GitHub.

## Visão Geral

A sincronização de labels garante que todos os repositórios da organização tenham as mesmas labels definidas no template `config/labels.yaml`, mantendo consistência entre repositórios.

## Comportamento Padrão (Modo Conservador)

Por padrão, a sincronização é **aditiva**:
- ✅ Cria labels que não existem
- ✅ Atualiza labels existentes (cor, descrição)
- ✅ **Preserva labels extras** (não remove labels que não estão no template)

## Modo Completo (Com Deleção)

Com a flag `--delete-extras`:
- ✅ Cria labels que não existem
- ✅ Atualiza labels existentes
- ⚠️ **Remove labels extras** (mantém apenas as do template)

## Uso

### Comando Básico
```bash
poetry run python main.py --sync-labels
```

### Com Deleção de Labels Extras
```bash
poetry run python main.py --sync-labels --delete-extras
```

### Repositórios Específicos
```bash
poetry run python main.py --sync-labels --repos "repo1,repo2"
```

## Estrutura do Template

O arquivo `config/labels.yaml` define as labels padrão:

```yaml
labels:
  - name: "bug"
    color: "d73a4a"
    description: "Algo não está funcionando corretamente"
    category: "type"
  - name: "enhancement"
    color: "a2eeef"
    description: "Nova funcionalidade ou melhoria"
    category: "type"
```

## ⚠️ Alertas Importantes

### Alteração de Nomes de Labels

**ATENÇÃO**: Se você alterar manualmente o nome de uma label existente (ex: "bug" → "bugs") sem atualizar o template, quando o script rodar:

1. A label "bugs" será **automaticamente removida** de todos os issues, no caso de rodar com o padrão de "--delete-extras"
2. A label "bug" será recriada conforme o template
3. **Todos os issues perderão a label**

### Recomendação para Mudanças

Se precisar alterar o nome de uma label:

1. **Criar** uma nova label com o nome desejado
2. **Aplicar** a nova label nos issues que tinham a antiga
3. **Remover** a label antiga apenas após a migração
4. **Atualizar** o template `config/labels.yaml`
5. **Executar** a sincronização

## Configuração

### Variáveis de Ambiente

```bash
GITHUB_ORG=splor-mg
GITHUB_LABELS_FILE=config/labels.yaml
```

### Autenticação

O sistema usa GitHub App para autenticação:
- `GITHUB_APP_ID`
- `GITHUB_APP_INSTALLATION_ID` 
- `GITHUB_APP_PRIVATE_KEY`

## Troubleshooting

### Erro: "Label não encontrada"
- Verifique se a label existe no template `config/labels.yaml`
- Confirme se o repositório tem permissões adequadas

### Erro: "Token inválido"
- Verifique as configurações do GitHub App
- Confirme se o App está instalado na organização

### Labels não sincronizadas
- Execute com `--verbose` para ver detalhes
- Verifique se o repositório não está arquivado
