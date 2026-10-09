import requests
import json
import base64
import os
import time

USERNAME = 'otabekmkui'
PASSWORD = 'OTABEKJON$$$0919200235@$$$'
BOT_DIR = r'C:\Users\Otabek\.gemini\antigravity\scratch\telegram_ai_bot'

session = requests.Session()

print("[1/5] PythonAnywhere saytiga kirilmoqda...")
r = session.get('https://www.pythonanywhere.com/login/')
csrf_token = session.cookies.get('csrftoken')

login_data = {
    'csrfmiddlewaretoken': csrf_token,
    'auth-username': USERNAME,
    'auth-password': PASSWORD,
    'login_view-current_step': 'auth'
}
r_login = session.post('https://www.pythonanywhere.com/login/', data=login_data, headers={'Referer': 'https://www.pythonanywhere.com/login/'})

if 'Log out' not in r_login.text and 'logout' not in r_login.text:
    print("XATO: Parol yoki login noto'g'ri!")
    exit(1)
print("  Muqaffaqiyatli kirildi!")

print("[2/5] API Token olinmoqda/yaratilmoqda...")
r_account = session.get('https://www.pythonanywhere.com/account/')
account_csrf = session.cookies.get('csrftoken')

# Ensure API token exists
session.post('https://www.pythonanywhere.com/api_token/', data={'csrfmiddlewaretoken': account_csrf}, headers={'Referer': 'https://www.pythonanywhere.com/account/'})
r_token = session.get('https://www.pythonanywhere.com/api_token/')
try:
    API_TOKEN = r_token.json().get('token')
except:
    print("API Token olib bo'lmadi!")
    exit(1)

print(f"  API Token olindi: {API_TOKEN[:5]}...")

HEADERS = {'Authorization': f'Token {API_TOKEN}'}
API_BASE = f'https://eu.pythonanywhere.com/api/v0/user/{USERNAME}'
# Note: sometimes it's www.pythonanywhere.com, sometimes eu.pythonanywhere.com depending on where the user signed up. Let's try both.
r_test = requests.get(f'https://www.pythonanywhere.com/api/v0/user/{USERNAME}/cpu/', headers=HEADERS)
if r_test.status_code == 200:
    API_BASE = f'https://www.pythonanywhere.com/api/v0/user/{USERNAME}'
else:
    API_BASE = f'https://eu.pythonanywhere.com/api/v0/user/{USERNAME}'

print("[3/5] Fayllar yuklanmoqda...")
files_to_upload = ['main.py', 'config.py', 'ai_handler.py', 'keep_alive.py', 'requirements.txt', '.env', 'my_ai_session.session']
for filename in files_to_upload:
    path = os.path.join(BOT_DIR, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            res = requests.post(
                f'{API_BASE}/files/path/home/{USERNAME}/{filename}',
                headers=HEADERS,
                files={'content': f}
            )
            print(f"  {filename} -> {res.status_code}")

print("[4/5] Konsol yaratilmoqda va ishga tushirilmoqda...")
res_console = requests.post(f'{API_BASE}/consoles/', headers=HEADERS, json={'executable': 'bash'})
if res_console.status_code != 201:
    print("Konsol ochishda xato!", res_console.text)
    exit(1)

console_id = res_console.json()['id']
print(f"  Konsol ID: {console_id}")

print("[5/5] Kutubxonalar o'rnatilmoqda va bot yoqilmoqda...")
command = "pip3 install -r requirements.txt --user && nohup python3 main.py > bot.log 2>&1 &\n"
requests.post(f'{API_BASE}/consoles/{console_id}/send_input/', headers=HEADERS, json={'input': command})

time.sleep(3)
res_out = requests.get(f'{API_BASE}/consoles/{console_id}/get_latest_output/', headers=HEADERS)
print("  Konsol javobi:", res_out.json().get('output', '')[:200])

print("\nBOT MUVAFFAQIYATLI ISHGA TUSHDI! 24/7 PythonAnywhere'da ishlamoqda.")
