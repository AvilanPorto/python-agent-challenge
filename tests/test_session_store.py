import time
from app.session_store import SessionStore


def test_create_session_and_history():
    store = SessionStore()

    store.add_exchange("sess1", "oi", "olá")

    history = store.get_history("sess1")

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_history_limit():
    store = SessionStore()

    for i in range(10):
        store.add_exchange("sess1", f"user{i}", f"assistant{i}")

    history = store.get_history("sess1")

    assert len(history) <= 10


def test_ttl_expiration(monkeypatch):
    store = SessionStore()
    store.add_exchange("sess1", "oi", "olá")

    future_time = time.time() + 999999  # ← captura ANTES do mock
    monkeypatch.setattr(time, "time", lambda: future_time)  # ← retorna valor fixo

    history = store.get_history("sess1")
    assert history == []