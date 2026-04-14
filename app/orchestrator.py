import logging
from app.tool import search_kb
from app.llm_client import call_llm
from app.session_store import session_store

logger = logging.getLogger(__name__)

FALLBACK_ANSWER = "Não encontrei informação suficiente na base para responder essa pergunta."


def orchestrate(message: str, session_id: str | None = None) -> dict:
    """
    Fluxo principal:
    1. Recupera histórico da sessão (se session_id fornecido)
    2. Chama a tool para buscar contexto relevante na KB
    3. Se não houver contexto suficiente, retorna fallback
    4. Monta o contexto e chama o LLM com histórico
    5. Valida a resposta do LLM
    6. Salva a troca no histórico da sessão
    7. Retorna answer + sources
    """

    # Passo 1: recuperar histórico da sessão
    history = session_store.get_history(session_id) if session_id else []
    if session_id:
        logger.info("Sessão '%s' — histórico com %d mensagens", session_id, len(history))
    else:
        logger.info("Sem session_id — chamada independente")

    # Passo 2: buscar contexto via tool
    logger.info("Iniciando orquestração para mensagem: '%s'", message[:50])

    
    # enriquecer busca com histórico
    search_input = message

    if history:
        last_user_msgs = [
            h["content"] for h in history if h["role"] == "user"
        ]
        search_input = " ".join(last_user_msgs[-2:] + [message])

    logger.debug("Busca enriquecida: %s", search_input)

    sections = search_kb(search_input)

    # Passo 3: fallback se não houver contexto
    if not sections:
        logger.info("Nenhum contexto encontrado na KB — retornando fallback")
        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }

    logger.info("Contexto encontrado: %s", [s["section"] for s in sections])

    # Passo 4: montar contexto para o LLM
    context = "\n\n".join(
        f"[Seção: {s['section']}]\n{s['content']}"
        for s in sections
    )

    # Passo 5: chamar o LLM com histórico
    try:
        answer = call_llm(message, context, history=history)
    except Exception as e:
        logger.error("Falha ao chamar LLM: %s", e)
        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }

    # Passo 6: validar resposta do LLM
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

    # Passo 7: salvar troca no histórico da sessão
    if session_id:
        session_store.add_exchange(session_id, message, answer)
        logger.info("Troca salva na sessão '%s'", session_id)

    logger.info("Resposta gerada com sucesso")
    return {
        "answer": answer,
        "sources": [{"section": s["section"]} for s in sections],
    }