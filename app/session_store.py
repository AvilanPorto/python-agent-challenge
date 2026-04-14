import time
import logging
from threading import Lock

logger = logging.getLogger(__name__)

# Configurações da sessão
MAX_HISTORY = 5       # máximo de trocas (user + assistant) por sessão
SESSION_TTL = 1800    # 30 minutos em segundos


class SessionStore:
    """
    Gerencia sessões em memória com histórico curto e TTL.
    Thread-safe via Lock.
    """

    def __init__(self):
        self._sessions: dict[str, dict] = {}
        self._lock = Lock()

    def get_history(self, session_id: str) -> list[dict]:
        """Retorna o histórico da sessão ou lista vazia se não existir ou expirada."""
        with self._lock:
            self._evict_expired()
            session = self._sessions.get(session_id)
            if not session:
                logger.debug("Sessão '%s' não encontrada ou expirada", session_id)
                return []
            logger.debug("Sessão '%s' encontrada com %d mensagens", session_id, len(session["history"]))
            return session["history"]

    def add_exchange(self, session_id: str, user_message: str, assistant_message: str) -> None:
        """Adiciona uma troca (user + assistant) ao histórico da sessão."""
        with self._lock:
            self._evict_expired()

            if session_id not in self._sessions:
                self._sessions[session_id] = {"history": [], "last_active": time.time()}
                logger.info("Nova sessão criada: '%s'", session_id)

            session = self._sessions[session_id]
            session["history"].append({"role": "user", "content": user_message})
            session["history"].append({"role": "assistant", "content": assistant_message})
            session["last_active"] = time.time()

            # Manter apenas as últimas MAX_HISTORY trocas (2 mensagens por troca)
            max_messages = MAX_HISTORY * 2
            if len(session["history"]) > max_messages:
                session["history"] = session["history"][-max_messages:]
                logger.debug("Sessão '%s' truncada para %d mensagens", session_id, max_messages)

    def _evict_expired(self) -> None:
        """Remove sessões expiradas. Deve ser chamado dentro do lock."""
        now = time.time()
        expired = [
            sid for sid, data in self._sessions.items()
            if now - data["last_active"] > SESSION_TTL
        ]
        for sid in expired:
            del self._sessions[sid]
            logger.info("Sessão expirada e removida: '%s'", sid)


# Instância global compartilhada entre requisições
session_store = SessionStore()