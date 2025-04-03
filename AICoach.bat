@echo off
cd /d %~dp0

:: 激活 Conda 环境（不依赖绝对路径，只要求 conda 在 PATH 中）
call conda activate aicoach

:: 查找当前环境中的 pythonw.exe
for /f %%i in ('where pythonw') do set PYTHONW=%%i

:: 使用 pythonw 静默启动
start "" "%PYTHONW%" "%~dp0Main.py"

exit
