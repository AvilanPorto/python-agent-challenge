import pytest
from app.tool import parse_sections, search_kb
from unittest.mock import patch

SAMPLE_MARKDOWN = """
## Composição

### Definição
Composição é quando uma função/classe utiliza outra instância para executar parte do trabalho.

### Quando usar
Use para reduzir acoplamento e facilitar teste unitário.

---

## Herança

### Definição
Herança permite que uma classe compartilhe atributos e comportamentos de outra.

### Quando usar
Use quando há semelhança forte de contrato e comportamento.

---

## Falta de contexto

### Definição
Situação em que a KB não cobre a pergunta com segurança.

### Observação curta
Responder com limitação explícita protege contra alucinação.
"""


# --- parse_sections ---

def test_parse_sections_retorna_lista():
    sections = parse_sections(SAMPLE_MARKDOWN)
    assert isinstance(sections, list)


def test_parse_sections_encontra_todas_secoes():
    sections = parse_sections(SAMPLE_MARKDOWN)
    nomes = [s["section"] for s in sections]
    assert "Composição" in nomes
    assert "Herança" in nomes
    assert "Falta de contexto" in nomes


def test_parse_sections_conteudo_nao_vazio():
    sections = parse_sections(SAMPLE_MARKDOWN)
    for s in sections:
        assert s["content"].strip() != ""


def test_parse_sections_markdown_vazio():
    sections = parse_sections("")
    assert sections == []


# --- search_kb ---

def test_search_kb_encontra_secao_relevante():
    with patch("app.tool.fetch_kb", return_value=SAMPLE_MARKDOWN):
        results = search_kb("O que é composição?")
    nomes = [s["section"] for s in results]
    assert "Composição" in nomes


def test_search_kb_retorna_vazio_sem_match():
    with patch("app.tool.fetch_kb", return_value=SAMPLE_MARKDOWN):
        results = search_kb("previsão do tempo amanhã")
    assert results == []


def test_search_kb_retorna_no_maximo_3_secoes():
    with patch("app.tool.fetch_kb", return_value=SAMPLE_MARKDOWN):
        results = search_kb("composição herança contexto acoplamento")
    assert len(results) <= 3


def test_search_kb_secao_mais_relevante_primeiro():
    with patch("app.tool.fetch_kb", return_value=SAMPLE_MARKDOWN):
        results = search_kb("composição acoplamento instância")
    assert results[0]["section"] == "Composição"