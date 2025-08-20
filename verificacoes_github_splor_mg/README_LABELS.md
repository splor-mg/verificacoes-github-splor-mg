# Gerenciador de Labels do GitHub

Este módulo fornece ferramentas para gerenciar labels do GitHub de forma uniforme em toda a organização.

## Funcionalidades

- **Labels Padrão**: Conjunto predefinido de labels organizadas por categoria
- **Aplicação Automática**: Aplica labels a repositórios específicos ou toda a organização
- **Sincronização**: Atualiza labels existentes para manter consistência
- **Configuração Personalizada**: Permite definir labels específicas para sua organização
- **Exportação/Importação**: Salva e carrega configurações de labels

## Estrutura das Labels

### Tipo
- `bug` - Algo não está funcionando corretamente
- `new-feature` - Nova funcionalidade ou melhoria planejada
- `chore` - Tarefas de manutenção e organização
- `documentation` - Melhorias ou adições à documentação
- `question` - Pergunta ou dúvida sobre o projeto

### Status
- `wontfix` - Issue não será corrigida ou implementada

### Eventos/Reuniões
- `meeting` - Relacionado a reuniões ou eventos

> **Nota:** As labels são baseadas no arquivo `labels.yaml` da organização e podem ser personalizadas conforme necessário.

## Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# Token de acesso do GitHub
GITHUB_TOKEN=seu_token_aqui

# Nome da organização
GITHUB_ORG=splor-mg
```

### 2. Obter Token do GitHub

1. Acesse [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Clique em "Generate new token (classic)"
3. Selecione os escopos necessários:
   - `repo` - Acesso completo aos repositórios
   - `admin:org` - Gerenciar organização
4. Copie o token e cole no arquivo `.env`

## Uso

### Script Principal

```bash
# Ver todas as labels padrão
python -m verificacoes_github_splor_mg.labels_manager

# Aplicar labels a um repositório específico
python -m verificacoes_github_splor_mg.labels_manager --repo nome-do-repo

# Aplicar labels a todos os repositórios
python -m verificacoes_github_splor_mg.labels_manager --all-repos

# Listar labels de um repositório
python -m verificacoes_github_splor_mg.labels_manager --list nome-do-repo

# Exportar configuração das labels
python -m verificacoes_github_splor_mg.labels_manager --export labels.json

# Importar configuração personalizada
python -m verificacoes_github_splor_mg.labels_manager --import labels.json --all-repos
```

### Script de Labels Personalizadas

```bash
# Executar script interativo para labels personalizadas
python -m verificacoes_github_splor_mg.custom_labels
```

## Exemplos de Uso

### 1. Aplicar Labels Padrão a Todos os Repositórios

```bash
python -m verificacoes_github_splor_mg.labels_manager --all-repos
```

### 2. Aplicar Labels a um Repositório Específico

```bash
python -m verificacoes_github_splor_mg.labels_manager --repo meu-projeto
```

### 3. Verificar Labels Existentes

```bash
python -m verificacoes_github_splor_mg.labels_manager --list meu-projeto
```

### 4. Usar Configuração Personalizada

```bash
# Primeiro, exporte as labels padrão
python -m verificacoes_github_splor_mg.labels_manager --export minhas_labels.json

# Edite o arquivo JSON conforme necessário
# Depois, importe e aplique
python -m verificacoes_github_splor_mg.labels_manager --import minhas_labels.json --all-repos
```

## Personalização

### Modificar Labels Padrão

Edite o método `get_standard_labels()` em `labels_manager.py`:

```python
def get_standard_labels(self) -> Dict[str, Dict]:
    return {
        "minha_label": {
            "color": "ff0000",
            "description": "Descrição da minha label"
        },
        # ... outras labels
    }
```

### Usar Script de Labels Personalizadas

1. Edite `custom_labels.py`
2. Modifique a função `get_custom_labels()`
3. Execute o script:
   ```bash
   python -m verificacoes_github_splor_mg.custom_labels
   ```

## Cores das Labels

As cores são definidas em hexadecimal (sem #). Exemplos:

- `d73a4a` - Vermelho
- `0e8a16` - Verde
- `1d76db` - Azul
- `fbca04` - Amarelo
- `7057ff` - Roxo
- `cc317c` - Rosa

## Segurança

- **Nunca** commite o arquivo `.env` com tokens reais
- Use tokens com escopos mínimos necessários
- Revogue tokens não utilizados
- Considere usar GitHub Apps para projetos em produção

## Troubleshooting

### Erro de Autenticação
- Verifique se o `GITHUB_TOKEN` está correto
- Confirme se o token tem os escopos necessários
- Verifique se o token não expirou

### Erro de Organização
- Confirme se o `GITHUB_ORG` está correto
- Verifique se você tem acesso à organização
- Confirme se o token tem permissão para a organização

### Labels Não Aplicadas
- Verifique se o repositório existe
- Confirme se você tem permissão para criar/editar labels
- Verifique se o repositório não está arquivado

## Contribuição

Para adicionar novas funcionalidades:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes se aplicável
5. Envie um Pull Request

## Licença

Este projeto está sob a mesma licença do repositório principal.
