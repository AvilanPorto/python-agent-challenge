import httpx
import re
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def fetch_kb() -> str:
    """Baixa o conteúdo da KB via HTTP."""
    logger.debug("Buscando KB em: %s", settings.kb_url)
    response = httpx.get(settings.kb_url, timeout=10)
    response.raise_for_status()
    logger.debug("KB baixada com sucesso (%d caracteres)", len(response.text))
    return response.text


def parse_sections(markdown: str) -> list[dict]:
    """Divide o Markdown em seções pelo heading ## e retorna lista de {section, content}."""
    sections = []
    current_section = None
    current_lines = []

    for line in markdown.splitlines():
        if line.startswith("## "):
            if current_section is not None:
                sections.append({
                    "section": current_section,
                    "content": "\n".join(current_lines).strip(),
                })
            current_section = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_section is not None:
        sections.append({
            "section": current_section,
            "content": "\n".join(current_lines).strip(),
        })

    logger.debug("Seções encontradas na KB: %s", [s["section"] for s in sections])
    return sections


def search_kb(message: str) -> list[dict]:
    """
    Busca seções relevantes da KB com base nas palavras da mensagem.
    Retorna lista de {section, content} ordenada por relevância.
    """
    markdown = fetch_kb()
    sections = parse_sections(markdown)

    STOPWORDS = {
        "que", "qual", "como", "quando", "onde", "por", "para", "com", "sem",
        "uma", "uns", "umas", "isso", "este", "esta", "esse", "essa", "num",
        "não", "sim", "mais", "menos", "mas", "pois", "então", "assim", "vai",
        "the", "what", "is", "are", "how", "why", "who", "can", "will", "do",
    }

    keywords = [
        re.sub(r'[^\w]', '', word).lower() for word in message.split()
        if len(re.sub(r'[^\w]', '', word)) > 3
        and re.sub(r'[^\w]', '', word).lower() not in STOPWORDS
    ]

    logger.debug("Keywords extraídas da mensagem: %s", keywords)

    scored = []
    for section in sections:
        text = (section["section"] + " " + section["content"]).lower()
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scored.append((score, section))

    scored.sort(key=lambda x: x[0], reverse=True)
    result = [section for _, section in scored[:3]]

    logger.debug("Seções relevantes encontradas: %s", [s["section"] for s in result])
    return result