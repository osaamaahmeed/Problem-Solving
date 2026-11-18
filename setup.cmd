@echo off
setlocal
cd /d "%~dp0"
echo.
echo === Problem Solving setup ===
echo.
echo [1/3] Git repo + auto-log hook
if not exist .git git init
git config core.hooksPath tools/hooks
echo.
echo [2/3] Notion token (saved to .env, which git ignores)
if exist .env (
  echo   .env already exists, keeping it.
  goto token_done
)
set /p "TOKEN=  Paste your Notion integration token and press Enter: "
> .env echo NOTION_TOKEN=%TOKEN%
echo   Saved.
:token_done
echo.
echo [3/3] Browser click listener (starts now and at every Windows login)
set "PYW=pyw -3"
where pyw >nul 2>nul || set "PYW=pythonw"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\problem-solving-listener.cmd"
> "%STARTUP%" echo @start "" %PYW% "%~dp0tools\ps.py" listen
start "" %PYW% "%~dp0tools\ps.py" listen
echo   Listener running on port 10045.
echo.
echo Done. In Competitive Companion's options, make sure port 10045 is enabled (add it under custom ports if needed).
pause
