@echo off
cd /d "%~dp0"
python tools\server.py || py tools\server.py
pause
