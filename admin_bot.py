import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import subprocess
import os
import threading

TOKEN = "8646755585:AAEbmHQW4919nlO0y6mOb69gChMuyAX_e0w"

ADMIN_FILE = "admin_id.txt"

def get_admin_id():
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "r") as f:
            content = f.read().strip()
            if content.isdigit():
                return int(content)
    return None

def set_admin_id(user_id):
    with open(ADMIN_FILE, "w") as f:
        f.write(str(user_id))

ADMIN_ID = get_admin_id()

bot = telebot.TeleBot(TOKEN)
userbot_process = None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global ADMIN_ID
    if ADMIN_ID is None:
        ADMIN_ID = message.from_user.id
        set_admin_id(ADMIN_ID)
        bot.reply_to(message, f"✅ Tabriklaymiz! Sizning ID raqamingiz ({ADMIN_ID}) doimiy qabul qilindi. Endi Pult faqat sizga bo'ysunadi!")
    
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Kechirasiz, siz ushbu botning administratori emassiz! 🚫")
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_start = KeyboardButton("▶️ AI ni Yoqish")
    btn_stop = KeyboardButton("⏸ AI ni O'chirish")
    btn_cmd = KeyboardButton("📝 AI ga Buyruq Berish")
    btn_clear = KeyboardButton("🗑 Buyruqni O'chirish")
    btn_status = KeyboardButton("📊 Status")
    btn_auth = KeyboardButton("📱 Akkaunt Ulash (QR)")
    btn_auth_sms = KeyboardButton("📲 Akkaunt Ulash (SMS)")
    markup.add(btn_start, btn_stop)
    markup.add(btn_cmd, btn_clear)
    markup.add(btn_status)
    markup.add(btn_auth, btn_auth_sms)
    
    bot.send_message(message.chat.id, "Boshqaruv Pultiga xush kelibsiz! \n\nPastdagi tugmalardan birini tanlang:", reply_markup=markup)


qr_password = None
qr_password_event = threading.Event()

def process_qr_password(message):
    global qr_password
    qr_password = message.text
    qr_password_event.set()

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    global userbot_process, ADMIN_ID
    
    if ADMIN_ID is None or message.from_user.id != ADMIN_ID:
        return
        
    text = message.text
    
    if text == "▶️ AI ni Yoqish":
        if userbot_process and userbot_process.poll() is None:
            bot.reply_to(message, "AI allaqachon ishlab turibdi! ⚡️")
        else:
            bot.reply_to(message, "AI ishga tushirilmoqda... ⏳")
            # Windows muhitida venv orqali python main.py yurgizish
            python_path = os.path.join("venv", "Scripts", "python.exe")
            if not os.path.exists(python_path):
                python_path = "python"
                
            userbot_process = subprocess.Popen([python_path, "main.py"])
            bot.reply_to(message, "✅ AI muvaffaqiyatli ishga tushdi va xabarlarni o'qishni boshladi!")
            
    elif text == "⏸ AI ni O'chirish":
        if userbot_process and userbot_process.poll() is None:
            userbot_process.terminate()
            userbot_process = None
            bot.reply_to(message, "🛑 AI to'xtatildi. Endi u xabarlarga javob bermaydi.")
        else:
            bot.reply_to(message, "AI shundoq ham o'chiq turibdi! 💤")
            
    elif text == "📝 AI ga Buyruq Berish":
        msg = bot.reply_to(message, "📝 Iltimos, AI ga o'zingizning yangi vaqtinchalik buyrug'ingizni yozing.\n(Masalan: 'Bugun bayram, hamma narsaga 20% chegirma qildik deb hammaga ayt' yoki 'Men bugun bandman, hammaga ertaga yozaman degin')")
        bot.register_next_step_handler(msg, process_live_instruction)
        
    elif text == "🗑 Buyruqni O'chirish":
        if os.path.exists("live_instruction.txt"):
            os.remove("live_instruction.txt")
        bot.reply_to(message, "🗑 Vaqtinchalik buyruq o'chirib tashlandi! AI endi odatdagi o'zini qoidalari bo'yicha ishlaydi.")
        
    elif text == "📊 Status":
        instruction = ""
        if os.path.exists("live_instruction.txt"):
            with open("live_instruction.txt", "r", encoding="utf-8") as f:
                instruction = f"\n\n🔥 Faol buyruq: {f.read().strip()}"
                
        if userbot_process and userbot_process.poll() is None:
            bot.reply_to(message, f"🟢 Holat: AI ISHLAMOQDA\n\n- Bot yangi xabarlarga javob beryapti.\n- Xotira va So'kinishni bloklash qismi faol.{instruction}")
        else:
            bot.reply_to(message, f"🔴 Holat: AI O'CHIRILGAN\n\n- Bot uxlayapti va hech kimga javob bermayapti.{instruction}")

    elif text == "📱 Akkaunt Ulash (QR)":
        if userbot_process and userbot_process.poll() is None:
            bot.reply_to(message, "⚠️ Oldin AIni to'xtatishingiz kerak! ('⏸ AI ni O'chirish' tugmasini bosing)")
            return
            
        bot.reply_to(message, "⏳ QR kod tayyorlanmoqda... Kuting.")
        
        def run_qr_auth():
            global qr_password
            python_path = os.path.join("venv", "Scripts", "python.exe")
            if not os.path.exists(python_path):
                python_path = "python"
                
            process = subprocess.Popen([python_path, "qr_auth.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line == "ALREADY_AUTHORIZED":
                    bot.send_message(message.chat.id, "✅ Bu profilingiz allaqachon botga ulangan! Boshqa ulash shart emas.")
                    break
                elif line == "QR_READY":
                    if os.path.exists("qr.png"):
                        with open("qr.png", "rb") as photo:
                            bot.send_photo(message.chat.id, photo, caption="📷 Ushbu QR kodni Telegram sozlamalaridagi (Settings -> Devices -> Link Desktop Device) orqali skaner qiling.\n\n(Vaqtingiz: 2 daqiqa)")
                elif line == "NEED_PASSWORD":
                    msg = bot.send_message(message.chat.id, "🔐 Akkauntingizda 2-bosqichli parol (Cloud Password) yoqilgan ekan. Iltimos, parolingizni kiriting:")
                    bot.register_next_step_handler(msg, process_qr_password)
                    qr_password_event.clear()
                    qr_password_event.wait(timeout=60)
                    
                    if qr_password:
                        process.stdin.write(qr_password + "\n")
                        process.stdin.flush()
                        qr_password = None
                    else:
                        process.stdin.write("\n")
                        process.stdin.flush()
                elif line == "SUCCESS":
                    bot.send_message(message.chat.id, "🎉 Tabriklaymiz! Akkaunt muvaffaqiyatli ulandi! Endi AIni bemalol yoqishingiz mumkin.")
                    if os.path.exists("qr.png"):
                        os.remove("qr.png")
                elif line.startswith("ERROR"):
                    bot.send_message(message.chat.id, f"❌ Xatolik yuz berdi yoki vaqt tugadi: {line}")
                    if os.path.exists("qr.png"):
                        os.remove("qr.png")
            
        threading.Thread(target=run_qr_auth).start()

    elif text == "📲 Akkaunt Ulash (SMS)":
        if userbot_process and userbot_process.poll() is None:
            bot.reply_to(message, "⚠️ Oldin AIni to'xtatishingiz kerak! ('⏸ AI ni O'chirish' tugmasini bosing)")
            return
            
        bot.reply_to(message, "⏳ SMS orqali ulanish boshlanmoqda...")
        
        def run_sms_auth():
            global qr_password
            python_path = os.path.join("venv", "Scripts", "python.exe")
            if not os.path.exists(python_path):
                python_path = "python"
                
            process = subprocess.Popen([python_path, "sms_auth.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line == "ALREADY_AUTHORIZED":
                    bot.send_message(message.chat.id, "✅ Bu profilingiz allaqachon botga ulangan! Boshqa ulash shart emas.")
                    break
                elif line == "NEED_PHONE":
                    msg = bot.send_message(message.chat.id, "📞 Telefon raqamingizni xalqaro formatda kiriting (masalan: +998901234567):")
                    bot.register_next_step_handler(msg, process_qr_password)
                    qr_password_event.clear()
                    qr_password_event.wait(timeout=60)
                    if qr_password:
                        process.stdin.write(qr_password + "\n")
                        process.stdin.flush()
                        qr_password = None
                    else:
                        process.stdin.write("\n")
                        process.stdin.flush()
                elif line == "NEED_CODE":
                    msg = bot.send_message(message.chat.id, "✉️ Telegram profilingizga borgan 5 xonali kodni yozing:")
                    bot.register_next_step_handler(msg, process_qr_password)
                    qr_password_event.clear()
                    qr_password_event.wait(timeout=60)
                    if qr_password:
                        process.stdin.write(qr_password + "\n")
                        process.stdin.flush()
                        qr_password = None
                    else:
                        process.stdin.write("\n")
                        process.stdin.flush()
                elif line == "NEED_PASSWORD":
                    msg = bot.send_message(message.chat.id, "🔐 Akkauntingizda 2-bosqichli parol (Cloud Password) yoqilgan ekan. Iltimos, parolingizni kiriting:")
                    bot.register_next_step_handler(msg, process_qr_password)
                    qr_password_event.clear()
                    qr_password_event.wait(timeout=60)
                    if qr_password:
                        process.stdin.write(qr_password + "\n")
                        process.stdin.flush()
                        qr_password = None
                    else:
                        process.stdin.write("\n")
                        process.stdin.flush()
                elif line == "SUCCESS":
                    bot.send_message(message.chat.id, "🎉 Tabriklaymiz! Akkaunt muvaffaqiyatli ulandi! Endi AIni bemalol yoqishingiz mumkin.")
                elif line.startswith("ERROR"):
                    bot.send_message(message.chat.id, f"❌ Xatolik yuz berdi: {line}")
            
        threading.Thread(target=run_sms_auth).start()

def process_live_instruction(message):
    if message.text:
        with open("live_instruction.txt", "w", encoding="utf-8") as f:
            f.write(message.text)
        bot.reply_to(message, f"✅ Buyruq qabul qilindi! Endi AI kelgan xabarlarga shu buyruqqa asoslanib javob beradi:\n\n\"{message.text}\"")
    else:
        bot.reply_to(message, "Matn yozmadingiz, bekor qilindi.")

if __name__ == "__main__":
    from keep_alive import keep_alive
    keep_alive()
    print("Pult ishga tushdi va Web Server yondi (Render.com uchun)...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Xato: {e}")
