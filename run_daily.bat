@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo. >> output\daily_run.log
echo ====================================================== >> output\daily_run.log
echo [START] %date% %time% >> output\daily_run.log
echo ====================================================== >> output\daily_run.log
python run_daily.py >> output\daily_run.log 2>&1
if errorlevel 1 (
    echo [ERROR] Pipeline failed on %date% at %time% >> output\daily_run.log
) else (
    echo [SUCCESS] Pipeline completed on %date% at %time% >> output\daily_run.log
)
