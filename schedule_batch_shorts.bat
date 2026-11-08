@echo off
chcp 65001 >nul
echo ============================================================
echo   CURIOUS BYTE — BATCH SCHEDULE PUBLISHER (EVERY 30 MINS)
echo ============================================================
echo.
echo This will generate a batch of Shorts in True 3D quality,
echo upload them to YouTube, schedule each one to premiere 30 minutes apart,
echo and immediately delete local videos and images to save disk space.
echo.
cd /d "%~dp0"
python schedule_batch_shorts.py --count 10 --interval 30 --start-delay 30
echo.
pause
