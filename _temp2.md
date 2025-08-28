Vou explicar detalhadamente como o script projects_panels.py funciona e quais comandos você pode usar:

## 🔍 O que o script faz:

O script `projects_panels.py` é uma ferramenta que:
1. **Conecta** na API do GitHub via GraphQL
2. **Extrai** todos os projetos (ProjectV2) de uma organização
3. **Coleta** informações de todos os campos de cada projeto
4. **Gera** um arquivo YAML com a estrutura completa dos projetos

## 🚀 Como usar:

### **Comando básico:**
```bash
python scripts/projects_panels.py
```
- Usa a organização padrão (`aid-pilot`)
- Salva o resultado em `docs/projects-panels-splor.yml`

### **Especificando organização:**
```bash
python scripts/projects_panels.py --org "splor-mg"
```
- Extrai projetos da organização `splor-mg`
- Salva no arquivo padrão

### **Especificando arquivo de saída:**
```bash
python scripts/projects_panels.py --output "meus-projetos.yml"
```
- Salva o resultado em `meus-projetos.yml`

### **Modo verboso (com mais detalhes):**
```bash
python scripts/projects_panels.py --verbose
```
- Mostra informações detalhadas durante a execução
- Útil para debug

### **Combinando opções:**
```bash
python scripts/projects_panels.py --org "splor-mg" --output "projetos-splor.yml" --verbose
```

## ⚙️ Configuração necessária:

### **1. Variáveis de ambiente (arquivo .env):**
```bash
GITHUB_TOKEN=seu_token_aqui
GITHUB_ORG=aid-pilot  # ou sua organização
```

### **2. Token GitHub:**
- Vá para: https://github.com/settings/tokens
- Gere um token com permissões:
  - ✅ `read:org` - Para ler projetos da organização
  - ✅ `repo` - Para acessar repositórios

## 📊 O que o script extrai:

### **Para cada projeto:**
- **ID interno** (ex: `PVT_abc123...`)
- **Número** (ex: `2`)
- **Nome** (ex: "Gestão à Vista Pilot 2")
- **Descrição** (se existir)

### **Para cada campo:**
- **ID interno** (ex: `PVTSSF_def456...`)
- **Nome** (ex: "Status", "Data Fim")
- **Tipo** (ex: `SINGLE_SELECT`, `DATE`, `TEXT`)

### **Para campos SINGLE_SELECT:**
- **Opções** com nome, descrição e cor
- Exemplo:
```yaml
options:
  - name: "Backlog"
    description: "Itens aguardando para serem priorizados"
    color: "#8B5CF6"
```

### **Para campos ITERATION:**
- **Iterações** com título, datas de início e fim

## 📁 Arquivo de saída:

O script gera um YAML com esta estrutura:
```yaml
version: 1
org: aid-pilot
projects:
  - name: "Nome do Projeto"
    number: 1
    id: "PVT_abc123..."
    fields:
      - name: "Status"
        id: "PVTSSF_def456..."
        dataType: "SINGLE_SELECT"
        options:
          - name: "Backlog"
            color: "#8B5CF6"
```

## 🔍 Exemplos práticos:

### **1. Extrair projetos da aid-pilot:**
```bash
cd /home/carloshob/projects/aid-pilot/verificacoes-github-splor-mg
python scripts/projects_panels.py
```

### **2. Extrair projetos da splor-mg:**
```bash
python scripts/projects_panels.py --org "splor-mg"
```

### **3. Salvar em arquivo customizado:**
```bash
python scripts/projects_panels.py --output "projetos-backup.yml"
```

### **4. Ver detalhes da execução:**
```bash
python scripts/projects_panels.py --verbose
```

## ⚠️ Possíveis erros:

### **Token inválido:**
```
❌ Missing required environment variable: GITHUB_TOKEN
```
**Solução:** Configure o `GITHUB_TOKEN` no arquivo `.env`

### **Organização não encontrada:**
```
❌ GraphQL errors: [{"message": "Could not resolve to an Organization"}]
```
**Solução:** Verifique se o nome da organização está correto

### **Sem permissão:**
```
❌ GraphQL errors: [{"message": "Resource not accessible by integration"}]
```
**Solução:** Verifique se o token tem permissão `read:org`

## 💡 Dicas de uso:

1. **Execute primeiro** para ver quantos projetos existem
2. **Use `--verbose`** para debug se algo der errado
3. **O arquivo é sobrescrito** a cada execução
4. **Mantenha backup** se quiser preservar configurações manuais
5. **Execute periodicamente** para manter o YAML atualizado

## 🔧 Como funciona internamente:

### **1. Conexão GraphQL:**
- Usa a API oficial do GitHub
- Faz queries paginadas para buscar todos os projetos
- Extrai informações detalhadas de cada campo

### **2. Processamento dos dados:**
- Formata campos especiais (SINGLE_SELECT, ITERATION)
- Preserva opções e configurações
- Mantém a estrutura hierárquica

### **3. Geração do YAML:**
- Cria arquivo com encoding UTF-8
- Preserva caracteres especiais (acentos, etc.)
- Mantém formatação legível

## 📋 Resumo da execução:

Quando executado, o script mostra:
```
📊 Buscando projetos da organização 'aid-pilot'...
✅ Encontrados 3 projetos

📋 Resumo da extração:
   Organização: aid-pilot
   Total de projetos: 3
   Total de campos: 15
   - Gestão à Vista Pilot 2 (#2): 6 campos
   - Projeto Exemplo A (#1): 5 campos
   - Projeto Exemplo B (#3): 4 campos

✅ YAML salvo em: docs/projects-panels-splor.yml
```

O script é perfeito para automatizar a extração de informações dos projetos e manter o arquivo YAML sempre atualizado com a estrutura real dos projetos no GitHub!
