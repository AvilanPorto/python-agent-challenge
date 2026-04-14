import pytest
from pydantic import ValidationError
from app.models import MessageRequest, MessageResponse, Source


# --- MessageRequest ---

def test_message_request_valido():
    req = MessageRequest(message="O que é composição?")
    assert req.message == "O que é composição?"


def test_message_request_com_session_id():
    req = MessageRequest(message="Olá", session_id="sessao-123")
    assert req.session_id == "sessao-123"


def test_message_request_sem_session_id():
    req = MessageRequest(message="Olá")
    assert req.session_id is None


def test_message_request_rejeita_vazio():
    with pytest.raises(ValidationError):
        MessageRequest(message="")


def test_message_request_rejeita_apenas_espacos():
    with pytest.raises(ValidationError):
        MessageRequest(message="   ")


# --- MessageResponse ---

def test_message_response_sucesso():
    resp = MessageResponse(
        answer="Composição é quando uma classe usa outra.",
        sources=[Source(section="Composição")],
    )
    assert resp.answer != ""
    assert len(resp.sources) == 1


def test_message_response_fallback():
    resp = MessageResponse(
        answer="Não encontrei informação suficiente na base para responder essa pergunta.",
        sources=[],
    )
    assert resp.sources == []