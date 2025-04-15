# Verificações GitHub

Scripts para extrair e sincronizar informações de organizações GitHub.

## Scripts Disponíveis

### 1. Listar Repositórios
```bash
python main.py --list-repos
```
Gera `docs/repos_list.csv` com todos os repositórios da organização.

### 2. Sincronizar Labels da Organização
```bash
python main.py --sync-org
```
Sincroniza labels padrão da organização baseado em `docs/labels.yaml`.

### 3. Sincronizar Labels nos Repositórios
```bash
python main.py --sync-repos
```
Sincroniza labels em todos os repositórios (cria, atualiza e **deleta labels extras**).

### 4. Executar Todas as Operações
```bash
python main.py --all
```

### 5. Modo Conservador (não deleta labels extras)
```bash
python main.py --sync-repos --no-delete-extras
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

**ATENÇÃO**: Ao atualizar o nome de uma label existente (por exemplo, alterar de "bug" para "bugs"), a label será **automaticamente removida de todos os issues** onde estava aplicada.

**O que acontece quando você altera:**
- **Nome da label**: A label é removida de todos os issues automaticamente
- **Descrição da label**: ✅ Não afeta os issues (mantém-se aplicada)
- **Cor da label**: ✅ Não afeta os issues (mantém-se aplicada)

## Instalação

```bash
pip install -r requirements.txt
```

## Organização

- **`scripts/`**: Scripts Python para extração de dados
- **`docs/`**: Arquivos CSV gerados e templates YAML
- **`.github/workflows/`**: Workflows GitHub Actions para automação
