import asyncio
import datetime
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from telethon import TelegramClient, events
from config import TG_API_ID, TG_API_HASH, GROUP_PROMPTS, build_system_prompt
from ai_handler import get_ai_response
import os

# Bot yongan vaqtni saqlab olamiz (eski xabarlarga javob bermaslik uchun)
START_TIME = datetime.datetime.now(datetime.timezone.utc)

import json
from telethon.tl.functions.contacts import BlockRequest

WARNINGS_FILE = "warnings.json"

def get_warnings(user_id):
    if not os.path.exists(WARNINGS_FILE):
        return 0
    with open(WARNINGS_FILE, "r") as f:
        data = json.load(f)
    return data.get(str(user_id), 0)

def add_warning(user_id):
    data = {}
    if os.path.exists(WARNINGS_FILE):
        with open(WARNINGS_FILE, "r") as f:
            data = json.load(f)
    uid = str(user_id)
    data[uid] = data.get(uid, 0) + 1
    with open(WARNINGS_FILE, "w") as f:
        json.dump(data, f)
    return data[uid]


# .env dan o'qilgan qiymatlarni int formatga o'tkazishga harakat qilamiz
try:
    API_ID = int(TG_API_ID) if TG_API_ID else None
except ValueError:
    API_ID = None
API_HASH = TG_API_HASH

# Agar API kalitlar topilmasa dasturni to'xtatish
if not API_ID or not API_HASH or API_HASH == "your_api_hash_here":
    print("Xatolik: TG_API_ID yoki TG_API_HASH sozlanmagan yoki noto'g'ri!")
    print("Iltimos, .env faylini to'ldiring. (Maslahat: .env.example faylini .env deb nomlang va ichini to'ldiring)")
    exit(1)

# Telegram mijozini yaratish
client = TelegramClient('my_ai_session', API_ID, API_HASH)

def save_log(chat_id, sender, text):
    """Xabarlarni matnli faylga saqlash uchun funksiya"""
    with open("chat_history.txt", "a", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text_clean = text.replace('\n', ' ')
        f.write(f"[{now}] Chat: {chat_id} | {sender}: {text_clean}\n")

@client.on(events.NewMessage)
async def my_event_handler(event):
    # Eski xabarlarga (bot yonguncha kelgan xabarlarga) javob bermaslik
    if event.message.date and event.message.date < START_TIME:
        return

    # O'zimiz yozgan xabarlarga javob bermaslik uchun
    if event.message.out:
        return

    chat_id = event.chat_id
    message_text = event.message.message

    # Agar xabar matni bo'lmasa (masalan stiker yoki rasm) o'tkazib yuborish
    if not message_text:
        return

    # 1. Shaxsiy xabarlar (lichka) uchun tekshiruv
    if event.is_private:
        print(f"[Lichka] {chat_id} dan xabar keldi: {message_text}")
        save_log(chat_id, "User", message_text)
        
        async with client.action(chat_id, 'typing'):
            system_prompt = build_system_prompt(chat_type="private")
            ai_reply = await get_ai_response(system_prompt, message_text, chat_id)
            
            if not ai_reply:
                return
                
            if "[HAKORAT]" in ai_reply:
                ai_reply = ai_reply.replace("[HAKORAT]", "").strip()
                warn_count = add_warning(chat_id)
                if warn_count >= 3:
                    await event.reply("Siz 3 marta ogohlantirish oldingiz va haqorat qilganingiz uchun bloklandingiz! 🚫")
                    await client(BlockRequest(id=chat_id))
                    print(f"[BLOCKED] {chat_id} bloklandi.")
                    return
                else:
                    ai_reply = f"⚠️ Ogohlantirish {warn_count}/3: Iltimos so'kinmang!\n\n" + ai_reply

            await event.reply(ai_reply)
            print(f"Lichkaga AI javob berdi: {ai_reply}\n")
            save_log(chat_id, "AI", ai_reply)
        return

    # 2. Guruh ID si sozlamalarda bor-yo'qligini tekshirish
    if event.is_group and chat_id in GROUP_PROMPTS:
        print(f"[Guruh: {chat_id}] xabar keldi: {message_text}")
        save_log(chat_id, "User (Group)", message_text)
        
        # O'qilmoqda (Typing...) statusini ko'rsatish
        async with client.action(chat_id, 'typing'):
            # AI dan javob olish
            system_prompt = build_system_prompt(chat_type="group", chat_id=chat_id)
            ai_reply = await get_ai_response(system_prompt, message_text, chat_id)
            
            if not ai_reply:
                return
                
            if "[HAKORAT]" in ai_reply:
                ai_reply = ai_reply.replace("[HAKORAT]", "").strip()
                # Guruhda sender kimligini bilish
                sender_id = event.sender_id
                if sender_id:
                    warn_count = add_warning(sender_id)
                    if warn_count >= 3:
                        ai_reply = f"⚠️ Foydalanuvchi qoidalarni 3 marta buzgani uchun javob berilmaydi."
                    else:
                        ai_reply = f"⚠️ Ogohlantirish {warn_count}/3: Iltimos so'kinmang!\n\n" + ai_reply

            # Javobni yuborish (reply qilib)
            await event.reply(ai_reply)
            print(f"AI javob berdi: {ai_reply}\n")
            save_log(chat_id, "AI", ai_reply)

async def main():
    print("Dastur ishga tushmoqda...")
    # Parol ko'rinadigan bo'lishi uchun maxsus lambda funksiya yozdik
    await client.start(password=lambda: input("Iltimos, Telegram 2-bosqichli parolingizni (Cloud password) kiriting (Parol ekranda ko'rinadi): "))
    
    # Barcha guruhlar ID sini konsolga chiqarish (sozlash uchun qulay)
    print("\n--- Siz a'zo bo'lgan guruhlar ro'yxati va ularning ID lari ---")
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            print(f"ID: {dialog.id} | Nomi: {dialog.name}")
    print("----------------------------------------------------------")
    print("Yuqoridagi ID lardan keraklilarini olib config.py faylidagi GROUP_PROMPTS ga qo'shing!\n")
    
    print("AI UserBot ishga tushdi! Belgilangan guruhlarni kuzatmoqda...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
