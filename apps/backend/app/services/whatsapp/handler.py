import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WhatsAppHandler:
    async def handle_webhook(self, payload: Dict[str, Any]):
        """
        Process incoming WhatsApp webhook events.
        Docs: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples
        """
        logger.info(f"Received webhook payload: {payload}")
        
        try:
            entries = payload.get("entry", [])
            for entry in entries:
                changes = entry.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    
                    if "messages" in value:
                        for message in value["messages"]:
                            await self._process_message(message, value.get("contacts", []))
                            
                    elif "statuses" in value:
                        # Message status update (sent, delivered, read)
                        pass
                        
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            raise e

    async def _process_message(self, message: Dict[str, Any], contacts: list):
        """Handle individual message based on type"""
        msg_type = message.get("type")
        from_number = message.get("from")
        
        logger.info(f"Processing {msg_type} message from {from_number}")
        
        if msg_type == "text":
            text_body = message["text"]["body"]
            logger.info(f"Text from {from_number}: {text_body}")
            # TODO: Integrate with CommandRouter or Agent here
            
        elif msg_type == "button":
            btn_text = message["button"]["text"]
            logger.info(f"Button click from {from_number}: {btn_text}")

whatsapp_handler = WhatsAppHandler()
