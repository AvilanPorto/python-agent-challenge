import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um assistente técnico que responde perguntas com base exclusivamente no contexto fornecido.

Regras:
- Responda apenas com base no contexto fornecido.
- Se o contexto não for suficiente, responda exatamente: "Não encontrei informação suficiente na base para responder essa pergunta."
- Seja direto e objetivo.
- Não invente informações que não estejam no contexto.
- Responda sempre em português.
"""


def call_llm(message: str, context: str, history: list[dict] | None = None) -> str:
    """
    Chama o LLM com a pergunta, contexto e histórico opcional da sessão.
    Retorna o texto da resposta.
    """
    user_prompt = f"""Contexto da base de conhecimento:
{context}

Pergunta: {message}
"""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Adiciona histórico da sessão antes da pergunta atual
    if history:
        messages.extend(history)
        logger.debug("Histórico de sessão incluído: %d mensagens", len(history))

    messages.append({"role": "user", "content": user_prompt})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.llm_api_key}",
    }

    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 512,
    }

    logger.debug("Chamando LLM: provider=%s model=%s", settings.llm_provider, settings.llm_model)

    response = httpx.post(
        f"{settings.llm_base_url}/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )

    logger.debug("Resposta do LLM: status=%d", response.status_code)
    response.raise_for_status()

    data = response.json()
    answer = data["choices"][0]["message"]["content"].strip()
    logger.debug("Resposta gerada com %d caracteres", len(answer))
    return answer