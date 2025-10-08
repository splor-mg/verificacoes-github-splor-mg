# Autenticação GitHub App

Este documento explica como funciona o sistema de autenticação via GitHub App no projeto.

## Visão Geral

O sistema usa **GitHub App** para autenticação, eliminando a necessidade de Personal Access Tokens (PATs). O processo envolve:

1. **JWT**: Gera um token JWT assinado com a chave privada do App
2. **Installation Token**: Troca o JWT por um token de instalação temporário
3. **API Calls**: Usa o token de instalação para chamadas à API

## Arquivo: `scripts/github_app_auth.py`

### Função Principal: `get_github_app_installation_token()`

```python
def get_github_app_installation_token() -> str:
    """
    Obtém um installation token usando envs:
      - GITHUB_APP_ID
      - GITHUB_APP_INSTALLATION_ID
      - GITHUB_APP_PRIVATE_KEY ou GITHUB_APP_PRIVATE_KEY_PATH
    """
```

### Processo de Autenticação

1. **Lê credenciais** das variáveis de ambiente
2. **Gera JWT** assinado com a chave privada
3. **Troca por token** de instalação via API
4. **Retorna token** para uso nas chamadas

### Variáveis de Ambiente Necessárias

```bash
# Obrigatórias
GITHUB_APP_ID=123456                    # ID numérico do GitHub App
GITHUB_APP_INSTALLATION_ID=789012      # ID da instalação do App

# Chave privada (uma das opções)
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----..."  # Conteúdo PEM
# OU
GITHUB_APP_PRIVATE_KEY_PATH="/path/to/private-key.pem"       # Caminho do arquivo
```

### Suporte a Formatos

**Chave privada inline:**
```bash
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----"
```

**Chave privada em base64:**
```bash
GITHUB_APP_PRIVATE_KEY="LS0tLS1CRUdJTi..."
```

**Chave privada em arquivo:**
```bash
GITHUB_APP_PRIVATE_KEY_PATH="/home/user/github-app-key.pem"
```

## Segurança

### JWT com Expiração Curta
- **Duração**: 60 segundos
- **Clock skew**: 5 segundos de folga
- **Algoritmo**: RS256

### Token de Instalação
- **Duração**: 1 hora (padrão GitHub)
- **Escopo**: Limitado às permissões do App
- **Renovação**: Automática a cada chamada

## Uso nos Scripts

### Exemplo Básico
```python
from scripts.github_app_auth import get_github_app_installation_token

# Obter token
token = get_github_app_installation_token()

# Usar em chamadas à API
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}
```

### Tratamento de Erros
```python
try:
    token = get_github_app_installation_token()
    print(f"Token obtido: {token[:8]}...")
except RuntimeError as e:
    print(f"Erro de autenticação: {e}")
    # Verificar variáveis de ambiente
```

## Troubleshooting

### Erro: "Missing GITHUB_APP_ID"
- Verifique se `GITHUB_APP_ID` está definida
- Confirme se o valor é numérico

### Erro: "Missing GITHUB_APP_INSTALLATION_ID"
- Verifique se `GITHUB_APP_INSTALLATION_ID` está definida
- Confirme se o App está instalado na organização

### Erro: "Private key file not found"
- Verifique o caminho em `GITHUB_APP_PRIVATE_KEY_PATH`
- Confirme se o arquivo existe e tem permissões de leitura

### Erro: "Failed to create installation token"
- Verifique se o App tem as permissões necessárias
- Confirme se o App está instalado na organização
- Teste com `--verbose` para mais detalhes

## Vantagens sobre PATs

1. **Segurança**: Tokens temporários (1h vs permanente)
2. **Escopo limitado**: Apenas permissões do App
3. **Auditoria**: Logs de uso do App
4. **Revogação**: Fácil desinstalação do App
5. **Organização**: Gerenciado centralmente

## Configuração do GitHub App

### Permissões Necessárias
- **Repository**: Contents (Read), Issues (Write), Metadata (Read)
- **Organization**: Members (Read)

### Eventos
- Issues
- Repository

### Instalação
1. Criar GitHub App
2. Instalar na organização
3. Configurar secrets
4. Testar autenticação
