Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "C:\Users\Otabek\.gemini\antigravity\scratch\telegram_ai_bot"
objShell.Run "cmd /c venv\Scripts\activate.bat && python main.py > bot_local.log 2>&1", 0, False
