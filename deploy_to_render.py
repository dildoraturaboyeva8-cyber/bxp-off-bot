import requests, os, base64

GH_TOKEN = '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'
RENDER_KEY = 'rnd_N1AauaeZ19xyXNgVzDETb98eoPa7'
REPO_NAME = 'telegram-ai-bot'
GH_HEADERS = {'Authorization': f'token {GH_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}

print('[1/4] GitHub private repo yaratilmoqda...')
res = requests.post('https://api.github.com/user/repos', headers=GH_HEADERS, json={'name': REPO_NAME, 'private': True})
if res.status_code not in (201, 422):
    print("Xato:", res.text)
    exit(1)

print('[2/4] Fayllar yuklanmoqda (faqat keraklilar)...')
files_to_upload = [
    'main.py', 'config.py', 'ai_handler.py', 'keep_alive.py', 
    'requirements.txt', '.env', 'my_ai_session.session'
]

# We also need a run.py to satisfy Render Web Service port binding
with open('run.py', 'w', encoding='utf-8') as f:
    f.write('''import asyncio, os
from aiohttp import web
import main

async def handle(request):
    return web.Response(text="Telegram AI Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
async def run_all():
    await start_web_server()
    await main.main()

if __name__ == '__main__':
    asyncio.run(run_all())
''')
files_to_upload.append('run.py')

for filename in files_to_upload:
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            content = base64.b64encode(f.read()).decode()
        
        # get sha if exists
        sha = None
        r_get = requests.get(f'https://api.github.com/repos/DesignerOtabek/{REPO_NAME}/contents/{filename}', headers=GH_HEADERS)
        if r_get.status_code == 200:
            sha = r_get.json()['sha']
            
        data = {'message': f'Add {filename}', 'content': content}
        if sha: data['sha'] = sha
        
        r = requests.put(f'https://api.github.com/repos/DesignerOtabek/{REPO_NAME}/contents/{filename}', headers=GH_HEADERS, json=data)
        print(f"  {filename} -> {r.status_code}")

print('[3/4] Render service yangilanmoqda...')
SVC_ID = 'srv-d9pktrad0e5s73cfv6t0'
R_HEADERS = {'Authorization': 'Bearer ' + RENDER_KEY, 'Accept': 'application/json', 'Content-Type': 'application/json'}

payload = {
    'name': 'telegram-ai-bot',
    'repo': f'https://github.com/DesignerOtabek/{REPO_NAME}',
    'serviceDetails': {
        'envSpecificDetails': {
            'buildCommand': 'pip install -r requirements.txt',
            'startCommand': 'python run.py'
        }
    }
}
r_update = requests.patch('https://api.render.com/v1/services/' + SVC_ID, headers=R_HEADERS, json=payload)
print('  Update:', r_update.status_code)

print('[4/4] Deploy boshlanmoqda...')
r_deploy = requests.post('https://api.render.com/v1/services/' + SVC_ID + '/deploys', headers=R_HEADERS)
print('  Deploy:', r_deploy.status_code)
