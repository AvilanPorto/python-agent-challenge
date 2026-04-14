# Python Agent Challenge

API em Python com orquestração de fluxo por IA e base de conhecimento em Markdown.

---

Este projeto implementa uma API em FastAPI com um fluxo de orquestração de perguntas e respostas baseado em uma base de conhecimento em Markdown e um modelo de linguagem (LLM).

A arquitetura foi desenhada com separação clara de responsabilidades entre os componentes, garantindo testabilidade, manutenibilidade e isolamento das camadas de negócio.

Arquitetura

O sistema é dividido em cinco módulos principais:

main.py: responsável pela interface HTTP e validação de entrada via Pydantic
orchestrator.py: coordena o fluxo principal da aplicação
tool.py: realiza a busca de contexto na base de conhecimento
llm_client.py: abstrai a comunicação com o provedor de LLM
session_store.py: gerencia histórico de conversas em memória

Essa separação garante que cada módulo tenha uma única responsabilidade e facilita substituições futuras, como troca de provedor de LLM ou mecanismo de armazenamento.

Fluxo de execução

O fluxo da aplicação segue os seguintes passos:

Recebimento da requisição no endpoint /messages
Validação do payload com Pydantic
Consulta à base de conhecimento via busca por palavras-chave
Montagem do contexto a partir das seções relevantes
Chamada ao LLM com contexto e histórico da sessão
Validação da resposta retornada pelo modelo
Persistência opcional do histórico da sessão em memória
Decisões técnicas

Foi adotada uma estratégia de busca por palavras-chave na base de conhecimento devido à simplicidade do domínio e ao tamanho reduzido do dataset. Essa abordagem reduz complexidade e evita dependência de modelos de embeddings.

O armazenamento de sessão foi implementado em memória com TTL e limite de histórico, garantindo controle básico de estado sem necessidade de infraestrutura externa.

A validação da resposta do LLM é feita na camada de orquestração para garantir consistência do contrato da API independentemente do comportamento do modelo.

Limitações e melhorias futuras

A solução atual possui limitações conhecidas:

armazenamento de sessão não persistente e não distribuído
ausência de busca semântica na base de conhecimento
ausência de cache para a KB
dependência direta de um provedor de LLM em tempo de execução

Como evolução natural, seria possível substituir a busca por embeddings semânticos, migrar o session store para Redis e adicionar mecanismos de cache e observabilidade.