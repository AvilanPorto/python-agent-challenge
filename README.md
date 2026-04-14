# Python Agent Challenge

API em Python com orquestração de fluxo por IA e base de conhecimento em Markdown.

---

## Sumário

- [Visão geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Fluxo principal](#fluxo-principal)
- [Decisões técnicas](#decisões-técnicas)
- [Regras de decisão do fluxo](#regras-de-decisão-do-fluxo)
- [Como executar](#como-executar)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Testes](#testes)
- [Contrato da API](#contrato-da-api)
- [Evoluções futuras](#evoluções-futuras)

---

## Visão geral

A solução expõe um endpoint único `POST /messages` que recebe uma pergunta, consulta uma base de conhecimento em Markdown via HTTP, e retorna uma resposta gerada por LLM com rastreabilidade por seção.

---

## Arquitetura

```
DesafioPythonLLM/
├── app/
│   ├── __init__.py
│   ├── config.py        # Leitura de variáveis de ambiente (pydantic-settings)
│   ├── llm_client.py    # Chamada ao LLM via API compatível com OpenAI
│   ├── main.py          # Borda de entrada HTTP — valida e encaminha
│   ├── models.py        # Schemas de entrada e saída (Pydantic)
│   ├── orchestrator.py  # Coordena o fluxo: tool → LLM → resposta
│   └── tool.py          # Busca contexto na KB via HTTP
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_orchestrator.py
│   └── test_tool.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pytest.ini
├── README.md
└── requirements.txt
```

Cada camada tem uma responsabilidade única:

- `main.py` recebe a requisição e delega — sem lógica de negócio
- `orchestrator.py` decide o fluxo — sem saber de HTTP ou LLM diretamente
- `tool.py` busca contexto — sem saber o que fazer com ele
- `llm_client.py` chama o LLM — sem saber de onde veio o contexto

---

## Fluxo principal

```
POST /messages
      │
      ▼
  Valida entrada (Pydantic)
      │
      ▼
  orchestrator.orchestrate(message)
      │
      ├── tool.search_kb(message)
      │       └── fetch_kb() → HTTP GET KB_URL
      │       └── parse_sections() → divide por ##
      │       └── filtra por keywords → retorna seções relevantes
      │
      ├── [sem contexto] → retorna fallback imediatamente
      │
      ├── monta contexto com seções encontradas
      │
      ├── llm_client.call_llm(message, context)
      │       └── POST LLM_BASE_URL/chat/completions
      │
      ├── valida resposta do LLM no código
      │
      └── retorna answer + sources
```

---

## Decisões técnicas

### Busca por palavra-chave

A tool usa busca por palavra-chave simples com filtro de stopwords em vez de busca semântica com embeddings. Essa escolha foi consciente para o escopo do desafio: a KB é pequena e as perguntas de validação usam os mesmos termos das seções.

A evolução natural seria usar `sentence-transformers` para gerar embeddings das seções na inicialização e comparar por similaridade cosine a cada requisição — cobrindo perguntas com paráfrases e sinônimos.

### Validação de saída no código

A resposta do LLM é validada no `orchestrator.py` independentemente do prompt. Respostas vazias, muito curtas ou que correspondam ao texto de fallback resultam no retorno padronizado com `sources: []`. Isso garante consistência do contrato mesmo com variações de comportamento do modelo.

### Provedor configurável

O `llm_client.py` usa a interface `/chat/completions` compatível com OpenAI. Qualquer provedor que implemente essa interface (Groq, Azure OpenAI, OpenRouter, Ollama) funciona sem alteração de código — basta ajustar `LLM_BASE_URL`, `LLM_MODEL` e `LLM_API_KEY` no `.env`.

### logging em vez de print

Todos os módulos usam o módulo `logging` com níveis semânticos (`DEBUG`, `INFO`, `WARNING`, `ERROR`). Em produção o nível pode ser ajustado para `INFO` para reduzir volume sem perder rastreabilidade de eventos importantes.

### Multi-stage build com CI local

O `Dockerfile` usa dois estágios: o primeiro roda os testes unitários durante o `docker build` — se algum teste falhar o build para e o container não sobe. O segundo estágio gera a imagem final limpa.

Esse padrão cobre a etapa de CI local. A evolução natural seria adicionar CD via GitHub Actions com deploy automático em AWS Elastic Beanstalk ou ECS após push na branch principal.

---

## Regras de decisão do fluxo

Estas são as regras que governam o comportamento do orquestrador:

**Quando chamar a tool:**
sempre, para toda mensagem recebida antes de qualquer outra ação.

**Como montar o contexto:**
concatenar o conteúdo das seções retornadas pela tool no formato `[Seção: nome]\nconteúdo`, separadas por linha em branco. Máximo de 3 seções por chamada.

**Quando retornar fallback:**
- se a tool não retornar nenhuma seção relevante
- se a chamada ao LLM lançar exceção
- se a resposta do LLM for vazia ou muito curta (menos de 5 caracteres)
- se a resposta do LLM for igual ao texto de fallback

**Texto exato do fallback:**
```
Não encontrei informação suficiente na base para responder essa pergunta.
```

---

## Como executar

### Pré-requisitos

- Docker Desktop instalado e rodando
- Chave de API de um provedor LLM compatível (OpenAI, Groq, etc.)

### Passos

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd python-agent-challenge

# 2. Criar o arquivo de variáveis
cp .env.example .env

# 3. Editar o .env com suas configurações
# LLM_API_KEY=sua_chave_aqui

# 4. Subir o ambiente (roda testes + build + start)
docker compose up -d --build

# 5. Acessar a documentação interativa
# http://localhost:8000/docs
```

Ou usando o Makefile:

```bash
make up    # sobe o ambiente
make down  # encerra o ambiente
make test  # roda testes unitários + validação de contrato
```

---

## Variáveis de ambiente

| Variável | Descrição | Exemplo |
|---|---|---|
| `KB_URL` | URL da base de conhecimento em Markdown | URL oficial do desafio |
| `LLM_PROVIDER` | Nome do provedor LLM | `groq`, `openai` |
| `LLM_MODEL` | Modelo a ser usado | `llama-3.1-8b-instant` |
| `LLM_BASE_URL` | URL base da API do provedor | `https://api.groq.com/openai/v1` |
| `LLM_API_KEY` | Chave de autenticação da API | `gsk_...` |
| `MEMORY_STORE` | Backend de memória para sessões (opcional) | vazio na entrega mínima |
| `HOST` | Host do servidor | `0.0.0.0` |
| `PORT` | Porta do servidor | `8000` |

---

## Testes

Os testes unitários rodam automaticamente durante o `docker build` via multi-stage. Para rodar manualmente com o container no ar:

```bash
docker compose exec api pytest tests/ -v
```

Cobertura atual — 21 testes:

| Módulo | Casos testados |
|---|---|
| `tool.py` | parse de seções, busca por keyword, fallback sem match, limite de resultados, ordenação por relevância |
| `orchestrator.py` | fallback sem contexto, fallback com LLM falhando, fallback com resposta vazia, sucesso com answer e sources |
| `models.py` | validação de message vazio, session_id opcional, formato de resposta |

---

## Contrato da API

### Requisição

```json
{
  "message": "O que é composição?",
  "session_id": "sessao-123"
}
```

`session_id` é opcional. Na entrega mínima cada chamada é independente.

### Resposta — sucesso

```json
{
  "answer": "Composição é quando uma função/classe utiliza outra instância para executar parte do trabalho.",
  "sources": [
    { "section": "Composição" }
  ]
}
```

### Resposta — sem contexto

```json
{
  "answer": "Não encontrei informação suficiente na base para responder essa pergunta.",
  "sources": []
}
```

### Documentação interativa

Disponível em `http://localhost:8000/docs` via Swagger UI gerado automaticamente pelo FastAPI.

---

## Evoluções futuras

- **Busca semântica:** substituir a busca por palavra-chave por embeddings com `sentence-transformers` e similaridade cosine para cobrir paráfrases e sinônimos
- **session_id:** implementar histórico curto por sessão com TTL usando Redis ou dicionário em memória
- **Retry no LLM:** adicionar retry com backoff exponencial para falhas transitórias da API
- **CD pipeline:** adicionar GitHub Actions para deploy automático em AWS Elastic Beanstalk após push na branch principal
- **Observabilidade:** adicionar métricas de latência e taxa de fallback com Prometheus