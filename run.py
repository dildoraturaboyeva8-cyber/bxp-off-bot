import asyncio, os
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
