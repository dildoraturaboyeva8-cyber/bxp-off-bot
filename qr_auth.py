import asyncio
import os
import qrcode
from telethon import TelegramClient
import telethon.errors
from config import TG_API_ID, TG_API_HASH

async def do_qr_login():
    api_id = int(TG_API_ID)
    api_hash = TG_API_HASH
    
    client = TelegramClient('my_ai_session', api_id, api_hash)
    await client.connect()
    
    if await client.is_user_authorized():
        await client.disconnect()
        return "ALREADY_AUTHORIZED"

    qr_login = await client.qr_login()
    
    # Generate QR Code image
    img = qrcode.make(qr_login.url)
    img.save("qr.png")
    
    print("QR_READY", flush=True) # Signifies admin_bot can read qr.png
    
    try:
        await qr_login.wait(timeout=120)
        await client.disconnect()
        return "SUCCESS"
    except telethon.errors.SessionPasswordNeededError:
        print("NEED_PASSWORD", flush=True)
        import sys
        password = sys.stdin.readline().strip()
        try:
            await client.sign_in(password=password)
            await client.disconnect()
            return "SUCCESS"
        except Exception as e:
            await client.disconnect()
            return f"ERROR: Parol xato bo'lishi mumkin: {str(e)}"
    except Exception as e:
        await client.disconnect()
        return f"ERROR: {str(e)}"

if __name__ == "__main__":
    result = asyncio.run(do_qr_login())
    if result != "QR_READY":
        print(result, flush=True)
