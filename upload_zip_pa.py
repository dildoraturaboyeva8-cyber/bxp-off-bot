import requests

USERNAME = 'otabekmkui'
PASSWORD = 'OTABEKJON$$$0919200235@$$$'
ZIP_PATH = r'C:\Users\Otabek\Desktop\telegram_ai_bot_deploy.zip'

session = requests.Session()
print("Logging in...")
session.get('https://www.pythonanywhere.com/login/')
csrf = session.cookies.get('csrftoken')
r_log = session.post('https://www.pythonanywhere.com/login/', data={
    'csrfmiddlewaretoken': csrf,
    'auth-username': USERNAME,
    'auth-password': PASSWORD,
    'login_view-current_step': 'auth'
}, headers={'Referer': 'https://www.pythonanywhere.com/login/'})

if 'Log out' not in r_log.text and 'logout' not in r_log.text:
    print("Login failed")
    exit(1)

print("Uploading ZIP file...")
csrf2 = session.cookies.get('csrftoken')
with open(ZIP_PATH, 'rb') as f:
    files = {'file': ('telegram_ai_bot_deploy.zip', f)}
    data = {'csrfmiddlewaretoken': csrf2}
    r_up = session.post(
        f'https://www.pythonanywhere.com/user/{USERNAME}/files/home/{USERNAME}/',
        data=data,
        files=files,
        headers={'Referer': f'https://www.pythonanywhere.com/user/{USERNAME}/files/home/{USERNAME}/'}
    )
    print("Upload status:", r_up.status_code)
