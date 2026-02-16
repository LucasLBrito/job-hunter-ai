from fastapi import APIRouter, Request, HTTPException, status, Response, Query
from app.core.config import settings
from app.services.whatsapp.handler import whatsapp_handler
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/webhook")
async def verify_webhook(
    mode: str = Query(alias="hub.mode"),
    token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge")
):
    """
    Webhook verification challenge from WhatsApp/Meta.
    """
    if mode and token:
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return Response(content=challenge, media_type="text/plain")
        else:
            logger.warning(f"Webhook verification failed. Token: {token}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Verification failed"
            )
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Missing parameters"
    )

@router.post("/webhook")
async def receive_webhook(request: Request):
    """
    Receive webhook events from WhatsApp.
    """
    try:
        payload = await request.json()
        await whatsapp_handler.handle_webhook(payload)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        # Always return 200 to WhatsApp to avoid retries, handling errors internally
        return {"status": "error", "detail": str(e)}
