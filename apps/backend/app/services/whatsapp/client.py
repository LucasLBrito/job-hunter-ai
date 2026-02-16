import httpx
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhatsAppClient:
    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self):
        self.token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        
    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def send_message(self, to: str, message: str) -> Optional[Dict[str, Any]]:
        """Send a free-form text message (only allowed within 24h window)"""
        if not self.token or not self.phone_number_id:
            logger.warning("WhatsApp credentials not configured")
            return None
            
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to send WhatsApp message: {e}")
                if hasattr(e, 'response') and e.response:
                    logger.error(f"Response: {e.response.text}")
                return None

    async def send_template(self, to: str, template_name: str, language_code: str = "pt_BR", components: list = None) -> Optional[Dict[str, Any]]:
        """Send a template message (required for initiating conversation)"""
        if not self.token or not self.phone_number_id:
            logger.warning("WhatsApp credentials not configured")
            return None
            
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }
        
        if components:
            payload["template"]["components"] = components
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to send WhatsApp template: {e}")
                return None

whatsapp_client = WhatsAppClient()
