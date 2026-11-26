@echo off
title StreamScope - Launch Power BI Dashboard
color 0B
echo ===================================================================
echo  StreamScope OTT Analytics - Power BI Dashboard Launcher
echo ===================================================================
echo.
echo Launching StreamScope_Analytics.pbip in Microsoft Power BI Desktop...
echo.
start "" "powerbi\StreamScope_Analytics.pbip"
if %errorlevel% equ 0 (
    echo [OK] Power BI Desktop launch initiated.
) else (
    echo [INFO] You can also open Power BI Desktop directly and select:
    echo   File -^> Open Report -^> Browse -^> powerbi\StreamScope_Analytics.pbip
)
echo.
timeout /t 3 >nul
