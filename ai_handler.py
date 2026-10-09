import os
import google.generativeai as genai

# Gemini API kalitini o'rnatamiz
GEMINI_API_KEY = "AQ.Ab8RN6I8SxtqQZbn2Ywg53aWRK4J9NkYO_16fuLKIiQa8ZKTTA"
genai.configure(api_key=GEMINI_API_KEY)

# Gemini Flash Lite - kuniga eng ko'p tekin xabarga ruxsat beruvchi model
model = genai.GenerativeModel('gemini-3.5-flash-lite')

# Har bir chat_id uchun xotirani (history) saqlaydigan lug'at
chat_histories = {}

async def get_ai_response(system_prompt, message, chat_id):
    try:
        # Agar bu foydalanuvchi bilan oldin gaplashmagan bo'lsak, xotirasini ochamiz
        if chat_id not in chat_histories:
            chat_histories[chat_id] = []
            
        # Foydalanuvchining yangi xabarini xotiraga qo'shamiz
        chat_histories[chat_id].append(f"User: {message}")
        
        # O'tgan barcha suhbatlar asosida javob olish (max 4 ta oxirgi xabarni beramiz)
        recent_history = chat_histories[chat_id][-4:]
        
        # Tizim qoidalari (System Prompt) va yozishmalar tarixini birlashtiramiz
        history_text = "\n".join(recent_history)
        
        # Vaqtinchalik buyruq (live_instruction.txt) ni o'qish
        live_instruction = ""
        if os.path.exists("live_instruction.txt"):
            with open("live_instruction.txt", "r", encoding="utf-8") as f:
                instruction = f.read().strip()
                if instruction:
                    live_instruction = f"\n\n==========================\n🔥 ADMINNING VAQTINCHALIK QAT'IY BUYRUG'I:\nShu buyruqqa asosan javob ber: {instruction}\n==========================\n"
        
        full_prompt = f"{system_prompt}{live_instruction}\n\nSUHBAT TARIXI:\n{history_text}\n\nAI (sen): "
        
        max_retries = 3
        retry_delay = 5 # boshlang'ich kutish vaqti
        
        for attempt in range(max_retries):
            try:
                # Gemini ga so'rov yuboramiz
                response = await model.generate_content_async(full_prompt)
                reply_text = response.text.strip()
                
                # AI ning javobini ham xotiraga saqlab qolamiz
                chat_histories[chat_id].append(f"AI: {reply_text}")
                return reply_text
                
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "rate limit" in error_msg or "quota" in error_msg or "resource_exhausted" in error_msg:
                    if attempt < max_retries - 1:
                        import asyncio
                        print(f"Limitga yetildi. {retry_delay} soniya kutilmoqda... (Urinish: {attempt+1})")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                
                # Boshqa xatoliklar bo'lsa yoki urinishlar tugasa
                import traceback
                with open("error.log", "a") as f:
                    f.write(f"Error: {e}\n{traceback.format_exc()}\n")
                print(f"AI Error: {e}")
                return None
                
        return None
    except Exception as e:
        import traceback
        with open("error.log", "a") as f:
            f.write(f"Outer Error: {e}\n{traceback.format_exc()}\n")
        return None
