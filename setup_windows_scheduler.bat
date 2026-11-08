@echo off
chcp 65001 >nul
echo ======================================================
echo    SCHEDULE CURIOUS BYTE DAILY SHORTS (WINDOWS)
echo ======================================================
echo.
echo This will schedule run_daily.bat to run every day at 10:00 AM automatically.
echo You can change the time anytime in Windows Task Scheduler.
echo.
set SCRIPT_PATH=wscript.exe \"%~dp0run_daily_silent.vbs\"
schtasks /create /tn "CuriousByte_DailyShort" /tr "%SCRIPT_PATH%" /sc daily /st 10:00 /f
echo.
if errorlevel 1 (
    echo [ERROR] Could not create scheduled task. Please right-click this script and choose "Run as administrator".
) else (
    echo [SUCCESS] Daily task 'CuriousByte_DailyShort' has been created for 10:00 AM every morning!
)
echo.
pause
