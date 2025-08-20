# Verificações GitHub splor-mg

Ferramenta para gerenciar e verificar repositórios da organização GitHub splor-mg.

## Funcionalidades

### 🏷️ Gerenciador de Labels
- **Labels Padrão**: Conjunto predefinido de labels organizadas por categoria
- **Aplicação Automática**: Aplica labels a repositórios específicos ou toda a organização
- **Sincronização**: Atualiza labels existentes para manter consistência
- **Configuração Personalizada**: Permite definir labels específicas para sua organização

### 🔍 Verificações de Repositórios
- Iteração sobre repositórios da organização
- Análise de issues e pull requests
- Verificações de configuração e compliance

## Estrutura do Projeto

```
verificacoes_github_splor_mg/
├── __init__.py
├── main.py                 # Script principal de verificações
├── labels_manager.py       # Gerenciador de labels
├── custom_labels.py        # Script de labels personalizadas
├── sync_labels.py          # Sincronização direta do YAML
├── yaml_to_labels.py       # Conversor YAML para JSON
├── test_labels.py          # Testes do gerenciador
└── README_LABELS.md        # Documentação específica das labels
```

## Configuração

### 1. Instalação das Dependências

```bash
# Usando Poetry (recomendado)
poetry install

# Ou usando pip
pip install -r requirements.txt
```

### 2. Configuração do GitHub

Crie um arquivo `.env` na raiz do projeto:

```bash
# Token de acesso do GitHub
GITHUB_TOKEN=seu_token_aqui

# Nome da organização
GITHUB_ORG=splor-mg
```

#### Obter Token do GitHub

1. Acesse [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Clique em "Generate new token (classic)"
3. Selecione os escopos necessários:
   - `repo` - Acesso completo aos repositórios
   - `admin:org` - Gerenciar organização
4. Copie o token e cole no arquivo `.env`

## Uso

### Gerenciador de Labels

#### Aplicar Labels Padrão

```bash
# A todos os repositórios
python -m verificacoes_github_splor_mg.labels_manager --all-repos

# A um repositório específico
python -m verificacoes_github_splor_mg.labels_manager --repo nome-do-repo

# Ver labels padrão
python -m verificacoes_github_splor_mg.labels_manager
```

#### Labels Personalizadas

```bash
# Executar script interativo
python -m verificacoes_github_splor_mg.custom_labels

# Sincronizar diretamente do labels.yaml
python -m verificacoes_github_splor_mg.sync_labels

# Exportar configuração atual
python -m verificacoes_github_splor_mg.labels_manager --export minhas_labels.json

# Importar configuração personalizada
python -m verificacoes_github_splor_mg.labels_manager --import minhas_labels.json --all-repos
```

#### Verificar Labels Existentes

```bash
# Listar labels de um repositório
python -m verificacoes_github_splor_mg.labels_manager --list nome-do-repo
```

### Script Principal

```bash
# Executar verificações principais
python -m verificacoes_github_splor_mg.main
```

### Testes

```bash
# Executar testes do gerenciador de labels
python -m verificacoes_github_splor_mg.test_labels
```

## Estrutura das Labels Padrão

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

## Exemplos de Uso

### 1. Configuração Inicial

```bash
# 1. Configure o arquivo .env
cp env.example .env
# Edite .env com suas credenciais

# 2. Aplique labels padrão a todos os repositórios
python -m verificacoes_github_splor_mg.labels_manager --all-repos

# OU use o script de sincronização direta do YAML
python -m verificacoes_github_splor_mg.sync_labels
```

### 2. Personalização de Labels

```bash
# 1. Exporte as labels padrão
python -m verificacoes_github_splor_mg.labels_manager --export labels_padrao.json

# 2. Edite o arquivo JSON conforme necessário

# 3. Aplique as labels personalizadas
python -m verificacoes_github_splor_mg.labels_manager --import labels_padrao.json --all-repos
```

### 3. Verificação de Labels

```bash
# Verificar labels em um repositório específico
python -m verificacoes_github_splor_mg.labels_manager --list meu-projeto

# Ver todas as labels padrão disponíveis
python -m verificacoes_github_splor_mg.labels_manager
```

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

## Documentação Adicional

- [README das Labels](verificacoes_github_splor_mg/README_LABELS.md) - Documentação detalhada do gerenciador de labels
- [Script de Labels Personalizadas](verificacoes_github_splor_mg/custom_labels.py) - Exemplo de configuração personalizada
- [Testes](verificacoes_github_splor_mg/test_labels.py) - Scripts de teste

## Licença

Este projeto está sob a mesma licença do repositório principal.
