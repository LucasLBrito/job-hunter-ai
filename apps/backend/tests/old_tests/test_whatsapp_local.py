import httpx
import asyncio
import logging

# Config
API_URL = "http://localhost:8001/api/v1"
VERIFY_TOKEN = "jobhunter_verify_token"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_verification():
    logger.info("Testing Webhook Verification...")
    async with httpx.AsyncClient() as client:
        # 1. Success case
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": VERIFY_TOKEN,
            "hub.challenge": "123456789"
        }
        res = await client.get(f"{API_URL}/whatsapp/webhook", params=params)
        if res.status_code == 200 and res.text == "123456789":
            logger.info("✅ Verification Success")
        else:
            logger.error(f"❌ Verification Failed: {res.status_code} - {res.text}")

        # 2. Failure case
        params["hub.verify_token"] = "wrong_token"
        res = await client.get(f"{API_URL}/whatsapp/webhook", params=params)
        if res.status_code == 403:
            logger.info("✅ Auth Check Success (Rejected wrong token)")
        else:
            logger.error(f"❌ Auth Check Failed: Should be 403, got {res.status_code}")

async def test_message_event():
    logger.info("\nTesting Webhook Message Event...")
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "12345",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "123456", "phone_number_id": "123456"},
                    "contacts": [{"profile": {"name": "Test User"}, "wa_id": "5511999999999"}],
                    "messages": [{
                        "from": "5511999999999",
                        "id": "wamid.HBgM",
                        "timestamp": "1700000000",
                        "text": {"body": "Ola, buscando vagas"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_URL}/whatsapp/webhook", json=payload)
        if res.status_code == 200:
            logger.info("✅ Message Handled Successfully")
        else:
            logger.error(f"❌ Message Handling Failed: {res.status_code} - {res.text}")

async def main():
    try:
        await test_verification()
        await test_message_event()
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
