import logging
from app.tool import search_kb
from app.llm_client import call_llm

logger = logging.getLogger(__name__)

FALLBACK_ANSWER = "Não encontrei informação suficiente na base para responder essa pergunta."


def orchestrate(message: str) -> dict:
    """
    Fluxo principal:
    1. Chama a tool para buscar contexto relevante na KB
    2. Se não houver contexto suficiente, retorna fallback
    3. Monta o contexto e chama o LLM
    4. Valida a resposta do LLM
    5. Retorna answer + sources
    """

    # Passo 1: buscar contexto via tool
    logger.info("Iniciando orquestração para mensagem: '%s'", message[:50])
    sections = search_kb(message)

    # Passo 2: fallback se não houver contexto
    if not sections:
        logger.info("Nenhum contexto encontrado na KB — retornando fallback")
        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }

    logger.info("Contexto encontrado: %s", [s["section"] for s in sections])

    # Passo 3: montar contexto para o LLM
    context = "\n\n".join(
        f"[Seção: {s['section']}]\n{s['content']}"
        for s in sections
    )

    # Passo 4: chamar o LLM
    try:
        answer = call_llm(message, context)
    except Exception as e:
        logger.error("Falha ao chamar LLM: %s", e)
        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }

    # Passo 5: validar resposta do LLM
    if not answer or len(answer.strip()) < 5:
        logger.warning("Resposta do LLM inválida ou muito curta — retornando fallback")
        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }

    if answer.strip() == FALLBACK_ANSWER:
        logger.info("LLM sinalizou falta de contexto — retornando fallback com sources vazios")
        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }

    # Passo 6: retornar resposta com sources
    logger.info("Resposta gerada com sucesso")
    return {
        "answer": answer,
        "sources": [{"section": s["section"]} for s in sections],
    }