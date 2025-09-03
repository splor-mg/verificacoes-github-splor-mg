
Na organização que trabalho foram criados vários projetos (https://github.com/orgs/minha-organização/projects).
Em alguns desses projetos foi criado um campo chamado "Data Fim". 


Eu quero criar um script para verificar o preenchimento desse campo "Data Fim" para os projetos desejados e nos quais o referido campo "Data Fim" existir. Vamos chamar a lista de projetos desejados/escolhidos como "PROJETOS_ESCOLHIDOS". 

Eu quero que o script verifique os issues de cada um dos repositórios listados em @repos_list.csv e, para aqueles issues que estejam associados a pelo menos um do(s) PROJETOS_ESCOLHIDOS, e nesses projetos exista o campo "Data Fim", eu quero que o script faça o seguinte:

 - caso o status do issue no projeto esteja diferente de "Done", eu quero que o campo "Data Fim" esteja vazio; se não estiver vazio, que apague o conteúdo dele
 - caso o status do issue no projeto esteja como "Done" e o campo "Data Fim" esteja em branco, eu quero que o campo "Data Fim" seja preenchido com a mesma data de fechamento do issue em questão
 - eu quero que o script faça o print as alterações que foram feitas



DEFAULT_ORG
DEFAULT_REPOS_FILE
DEFAULT_PROJECTS_FILE
DEFAULT_FIELD_NAME



Analisando o issues_close_date.py e o main.py, vejo que seria interessante integrar a funcionalidade de sincronização de datas de fechamento. Aqui estão os comandos que eu sugeriria adicionar ao main.py:

## 🆕 **Novos comandos para integrar:**

### 1. **`--sync-close-dates`** - Sincronizar datas de fechamento
```bash
python main.py --sync-close-dates
```

### 2. **`--project-number`** - Especificar número do projeto
```bash
python main.py --sync-close-dates --project-number 13
```

### 3. **`--field-name`** - Especificar nome do campo de data
```bash
python main.py --sync-close-dates --field-name "Data Fim"
```

### 4. **`--issue-node-id`** - Para sincronização específica
```bash
python main.py --sync-close-dates --issue-node-id "MDU6SXNzdWUxMjM="
```

### 5. **`--closed-at`** - Para sincronização específica
```bash
python main.py --sync-close-dates --closed-at "2025-08-27T20:49:00Z"
```

## 🔄 **Integração com comandos existentes:**

### **`--all`** - Incluir sincronização de datas
```bash
python main.py --all  # Executa tudo + sincronização de datas
```

### **`--verbose`** - Logs detalhados
```bash
python main.py --sync-close-dates --verbose
```

## 📋 **Estrutura sugerida no main.py:**

```python
# Argumentos adicionais
parser.add_argument('--sync-close-dates', action='store_true',
                   help='Sincroniza datas de fechamento nos projetos')
parser.add_argument('--project-number', type=int,
                   help='Número do projeto GitHub (ex: 13)')
parser.add_argument('--field-name', default='Data Fim',
                   help='Nome do campo de data no projeto')
parser.add_argument('--issue-node-id',
                   help='Node ID específico do issue para sincronizar')
parser.add_argument('--closed-at',
                   help='Data de fechamento específica (ISO format)')

# Lógica de execução
if args.all or args.sync_close_dates:
    # Executar sincronização de datas de fechamento
    # Usar as funções do issues_close_date.py
```

## 🎯 **Vantagens da integração:**

1. **Centralização**: Tudo em um só comando
2. **Consistência**: Mesmo padrão de argumentos
3. **Flexibilidade**: Pode ser usado isoladamente ou com `--all`
4. **Reutilização**: Aproveita as configurações existentes (token, org, etc.)

## 🔧 **Implementação sugerida:**

```python
# Importar funções do issues_close_date.py
from scripts.issues_close_date import (
    get_project_and_field_ids,
    get_or_find_project_item_id_for_issue,
    update_date_field,
    _iso_date
)

# Na função main(), adicionar:
if args.all or args.sync_close_dates:
    try:
        print(f"\n📅 Sincronizando datas de fechamento para projeto: {args.project_number or 'padrão'}")
        
        # Se não foi especificado projeto, usar padrão
        project_number = args.project_number or 13
        field_name = args.field_name or 'Data Fim'
        
        # Obter IDs do projeto e campo
        project_id, field_id = get_project_and_field_ids(
            config['github_token'], 
            config['github_org'], 
            project_number, 
            field_name
        )
        
        print(f"✅ Projeto {project_number} e campo '{field_name}' identificados")
        
        # Se foram especificados issue específico e data
        if args.issue_node_id and args.closed_at:
            # Sincronização específica
            item_id = get_or_find_project_item_id_for_issue(
                config['github_token'], 
                args.issue_node_id, 
                project_id
            )
            
            if item_id:
                date_value = _iso_date(args.closed_at)
                update_date_field(
                    config['github_token'], 
                    project_id, 
                    item_id, 
                    field_id, 
                    date_value
                )
                print(f"✅ Campo '{field_name}' atualizado para {date_value}")
            else:
                print("⚠️  Issue não está vinculado ao projeto especificado")
        else:
            print("💡 Para sincronização específica, use --issue-node-id e --closed-at")
            print("💡 Para sincronização em lote, implementar lógica adicional")
            
    except Exception as e:
        print(f"❌ Erro na sincronização de datas: {e}")
        logging.error(f"Erro na sincronização de datas: {e}")
        success = False
```
