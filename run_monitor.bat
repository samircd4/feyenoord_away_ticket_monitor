@echo off
title Feyenoord Ticket Monitor
echo =======================================================
echo           FEYENOORD AWAY TICKET MONITOR
echo =======================================================
echo.
echo Starting ticket monitor...
echo (Press Ctrl + C in this window anytime to stop)
echo.

uv run main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 'uv' command failed or not found. Falling back to python...
    python main.py
)

echo.
echo Monitor has stopped.
pause
