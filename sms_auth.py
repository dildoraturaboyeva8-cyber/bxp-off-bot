import sys
import asyncio
from telethon import TelegramClient
import telethon.errors
from config import TG_API_ID, TG_API_HASH

async def do_sms_login():
    api_id = int(TG_API_ID)
    api_hash = TG_API_HASH
    
    client = TelegramClient('my_ai_session', api_id, api_hash)
    await client.connect()
    
    if await client.is_user_authorized():
        await client.disconnect()
        return "ALREADY_AUTHORIZED"
        
    print("NEED_PHONE", flush=True)
    phone = sys.stdin.readline().strip().replace(" ", "").replace("-", "").replace("+", "")
    phone = "+" + phone
    if not phone or phone == "+":
        await client.disconnect()
        return "ERROR: Telefon raqam kiritilmadi."
    
    try:
        sent_code = await client.send_code_request(phone)
        print("NEED_CODE", flush=True)
        code = sys.stdin.readline().strip()
        if not code:
            await client.disconnect()
            return "ERROR: Kod kiritilmadi."
        
        try:
            await client.sign_in(phone, code, phone_code_hash=sent_code.phone_code_hash)
            await client.disconnect()
            return "SUCCESS"
        except telethon.errors.SessionPasswordNeededError:
            print("NEED_PASSWORD", flush=True)
            password = sys.stdin.readline().strip()
            if not password:
                await client.disconnect()
                return "ERROR: Parol kiritilmadi."
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
    result = asyncio.run(do_sms_login())
    if result:
        print(result, flush=True)
