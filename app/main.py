import logging
from fastapi import FastAPI, HTTPException
from app.models import MessageRequest, MessageResponse, Source
from app.orchestrator import orchestrate

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Python Agent Challenge",
    description="API com orquestração de fluxo por IA e base de conhecimento em Markdown.",
    version="1.0.0",
)


@app.post("/messages", response_model=MessageResponse)
async def messages(request: MessageRequest) -> MessageResponse:
    logger.info("Requisição recebida: message='%s'", request.message[:50])
    try:
        result = orchestrate(request.message)
        return MessageResponse(
            answer=result["answer"],
            sources=[Source(section=s["section"]) for s in result["sources"]],
        )
    except Exception as e:
        logger.error("Erro inesperado no endpoint: %s", e)
        raise HTTPException(status_code=500, detail=str(e))