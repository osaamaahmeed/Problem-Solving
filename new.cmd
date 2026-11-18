@echo off
rem Start a problem:  .\new <problem-url>
where py >nul 2>nul && (py -3 "%~dp0tools\ps.py" new %*) || (python "%~dp0tools\ps.py" new %*)
