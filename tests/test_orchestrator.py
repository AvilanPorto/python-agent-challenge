import pytest
from unittest.mock import patch
from app.orchestrator import orchestrate, FALLBACK_ANSWER


MOCK_SECTIONS = [
    {
        "section": "Composição",
        "content": "Composição é quando uma função/classe utiliza outra instância.",
    }
]

MOCK_ANSWER = "Composição é quando uma função utiliza outra instância para executar parte do trabalho."


# --- fallback ---

def test_orchestrate_retorna_fallback_sem_contexto():
    with patch("app.orchestrator.search_kb", return_value=[]):
        result = orchestrate("previsão do tempo")
    assert result["answer"] == FALLBACK_ANSWER
    assert result["sources"] == []


def test_orchestrate_retorna_fallback_quando_llm_falha():
    with patch("app.orchestrator.search_kb", return_value=MOCK_SECTIONS):
        with patch("app.orchestrator.call_llm", side_effect=Exception("LLM indisponível")):
            result = orchestrate("O que é composição?")
    assert result["answer"] == FALLBACK_ANSWER
    assert result["sources"] == []


def test_orchestrate_retorna_fallback_quando_llm_responde_vazio():
    with patch("app.orchestrator.search_kb", return_value=MOCK_SECTIONS):
        with patch("app.orchestrator.call_llm", return_value=""):
            result = orchestrate("O que é composição?")
    assert result["answer"] == FALLBACK_ANSWER
    assert result["sources"] == []


def test_orchestrate_retorna_fallback_quando_llm_sinaliza_falta_de_contexto():
    with patch("app.orchestrator.search_kb", return_value=MOCK_SECTIONS):
        with patch("app.orchestrator.call_llm", return_value=FALLBACK_ANSWER):
            result = orchestrate("O que é composição?")
    assert result["answer"] == FALLBACK_ANSWER
    assert result["sources"] == []


# --- sucesso ---

def test_orchestrate_retorna_answer_e_sources():
    with patch("app.orchestrator.search_kb", return_value=MOCK_SECTIONS):
        with patch("app.orchestrator.call_llm", return_value=MOCK_ANSWER):
            result = orchestrate("O que é composição?")
    assert result["answer"] == MOCK_ANSWER
    assert len(result["sources"]) == 1
    assert result["sources"][0]["section"] == "Composição"


def test_orchestrate_sources_contem_apenas_section():
    with patch("app.orchestrator.search_kb", return_value=MOCK_SECTIONS):
        with patch("app.orchestrator.call_llm", return_value=MOCK_ANSWER):
            result = orchestrate("O que é composição?")
    for source in result["sources"]:
        assert list(source.keys()) == ["section"]