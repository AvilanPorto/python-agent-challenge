from urllib import response

import httpx
from app.config import settings

SYSTEM_PROMPT = """Você é um assistente técnico que responde perguntas com base exclusivamente no contexto fornecido.

Regras:
- Responda apenas com base no contexto fornecido.
- Se o contexto não for suficiente, responda exatamente: "Não encontrei informação suficiente na base para responder essa pergunta."
- Seja direto e objetivo.
- Não invente informações que não estejam no contexto.
- Responda sempre em português.
"""


def call_llm(message: str, context: str) -> str:
    """
    Chama o LLM com a pergunta e o contexto recuperado da KB.
    Retorna o texto da resposta.
    """
    user_prompt = f"""Contexto da base de conhecimento:
{context}

Pergunta: {message}
"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.llm_api_key}",
    }

    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 512,
    }

    response = httpx.post(
        f"{settings.llm_base_url}/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )

    print(f"[DEBUG] LLM status: {response.status_code}")
    print(f"[DEBUG] LLM response: {response.text}")

    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()