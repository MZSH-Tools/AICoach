@echo off
cd /d %~dp0
call conda activate aicoach
for /f %%i in ('where pythonw') do set PYTHONW=%%i
start "" "%PYTHONW%" "%~dp0Main.py"
exit
