@echo off
chcp 65001 >nul
title Curious Byte Unique - Autonomous Daily Pipeline 2.0 (48 Videos / 24h Cadence)
echo ===========================================================================
echo   CURIOUS BYTE UNIQUE - AUTONOMOUS VIRAL SHORTS ENGINE 2.0
echo   Daily 24-Hour Schedule: 12:00 AM to 11:30 PM (Every 30 Minutes)
echo   100% PUBLIC Release Cadence - 10 Scenes Per Short - Zero Faces, Zero Text
echo ===========================================================================
echo.

python run_autonomous_scheduler.py --count 48 --interval 30 --start-at midnight

echo.
echo ===========================================================================
echo   Execution Finished. Full schedule reports saved in output/metadata/
echo ===========================================================================
pause
