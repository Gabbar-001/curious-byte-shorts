@echo off
chcp 65001 >nul
cd /d "%~dp0"
python upload_true3d.py
pause
