# CRUD de Alunos — Firebase Cloud Firestore (Python)

Atividade prática da aula de **Banco de Dados NoSQL**. Projeto em Python que implementa
`CREATE`, `READ`, `UPDATE` e `DELETE` na coleção `alunos` do Cloud Firestore, com
consultas por **turma** e por **data de nascimento**.

Duas interfaces estão disponíveis no mesmo projeto:

- **Menu no terminal** — `python main.py`
- **API REST (FastAPI)** — `uvicorn api:app --reload` (documentação automática em `/docs`)

## Estrutura do projeto

```
.
├── main.py                 # entrada do menu no terminal
├── api.py                  # entrada da API (uvicorn api:app)
├── app/
│   ├── config.py           # inicialização do Firebase Admin SDK
│   ├── models.py           # validação dos dados (Pydantic)
│   ├── repository.py       # CREATE / READ / UPDATE / DELETE + consultas
│   ├── cli.py              # menu no terminal
│   └── rest_api.py         # rotas da API REST
├── tests/                  # testes com Firestore falso em memória
├── .env.example            # modelo de configuração
├── .gitignore              # protege serviceAccountKey.json e .env
└── requirements.txt
```

## Estrutura da coleção `alunos`

| Campo            | Tipo    | Exemplo       |
|------------------|---------|---------------|
| `nome`           | string  | `"Ana"`       |
| `turma`          | string  | `"3DSB"`      |
| `dataNascimento` | string  | `"2009-05-15"`|
| `ativo`          | boolean | `true`        |

O ID de cada documento é gerado automaticamente pelo Firestore.

## 1. Configurar o Firebase

1. Acesse o [Console do Firebase](https://console.firebase.google.com/) e crie um projeto.
2. No menu **Build › Firestore Database**, clique em **Criar banco de dados**.
3. Em **Configurações do projeto › Contas de serviço**, gere uma nova chave privada.
4. Salve o arquivo baixado na raiz do projeto com o nome `serviceAccountKey.json`.
5. Copie o modelo de configuração e ajuste, se necessário:

```bash
cp .env.example .env
```

Conteúdo padrão do `.env`:

```env
SERVICE_ACCOUNT_KEY=./serviceAccountKey.json
```

> ⚠️ **Nunca envie `serviceAccountKey.json` nem `.env` para o GitHub.** O `.gitignore`
> já está configurado para impedir isso. Use apenas dados fictícios.

## 2. Instalar as dependências

Requer Python 3.8 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Executar o menu no terminal

```bash
python main.py
```

Menu disponível:

```
1 - Cadastrar aluno (CREATE)
2 - Listar todos os alunos (READ)
3 - Buscar aluno por ID
4 - Atualizar aluno (UPDATE)
5 - Excluir aluno (DELETE)
6 - Consultar por turma
7 - Consultar por data de nascimento
8 - Consultar por turma E data
0 - Sair
```

## 4. Executar a API REST

```bash
uvicorn api:app --reload
```

Acesse **http://127.0.0.1:8000/docs** para testar os endpoints pelo Swagger UI.

| Método | Endpoint                                  | Descrição                         |
|--------|-------------------------------------------|-----------------------------------|
| POST   | `/alunos`                                 | Cadastrar aluno (CREATE)          |
| GET    | `/alunos`                                 | Listar todos (READ)               |
| GET    | `/alunos?turma=3DSB`                      | Filtrar por turma                 |
| GET    | `/alunos?dataNascimento=2009-05-15`       | Filtrar por data                  |
| GET    | `/alunos/turma/{turma}`                   | Consultar por turma               |
| GET    | `/alunos/data-nascimento/{data}`          | Consultar por data de nascimento  |
| GET    | `/alunos/{aluno_id}`                      | Buscar por ID                     |
| PUT    | `/alunos/{aluno_id}`                      | Atualizar aluno (UPDATE)          |
| PATCH  | `/alunos/{aluno_id}`                      | Atualização parcial               |
| DELETE | `/alunos/{aluno_id}`                      | Excluir aluno (DELETE) → 204      |

Exemplos com `curl`:

```bash
# CREATE
curl -X POST http://127.0.0.1:8000/alunos \
  -H "Content-Type: application/json" \
  -d '{"nome":"Ana","turma":"3DSB","dataNascimento":"2009-05-15","ativo":true}'

# READ (todos)
curl http://127.0.0.1:8000/alunos

# UPDATE
curl -X PATCH http://127.0.0.1:8000/alunos/ID_DO_DOCUMENTO \
  -H "Content-Type: application/json" \
  -d '{"turma":"4DSA"}'

# DELETE
curl -X DELETE http://127.0.0.1:8000/alunos/ID_DO_DOCUMENTO

# Consulta combinada
curl "http://127.0.0.1:8000/alunos?turma=3DSB&dataNascimento=2009-05-15"
```

## 5. Executar os testes (sem Firebase)

Os testes usam um Firestore falso em memória, então não precisam de chave de acesso:

```bash
python -m unittest discover -v
```

## 6. Usar o emulador local do Firestore (opcional)

Permite desenvolver sem uma chave real:

```bash
gcloud beta emulators firestore start --host-port=localhost:8080
```

No `.env`:

```env
FIRESTORE_EMULATOR_HOST=localhost:8080
FIRESTORE_PROJECT_ID=demo-sla
```

## Entrega

- [ ] Link do repositório GitHub (sem `serviceAccountKey.json`).
- [ ] Capturas de tela do CRUD no terminal.
- [ ] Capturas de tela do CRUD na API (`/docs`).
- [ ] Capturas das consultas por turma e por data de nascimento.

## Observações de segurança

- Dados fictícios, conforme pedido na atividade.
- Conta de serviço com permissões mínimas (**Cloud Datastore User** é suficiente para esta atividade).
- Em produção, use variáveis de ambiente ou um gerenciador de segredos em vez de arquivos locais.
