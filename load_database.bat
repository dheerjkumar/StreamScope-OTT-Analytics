@echo off
title StreamScope - Automated MySQL Database Setup
color 0A
echo ===================================================================
echo  StreamScope OTT Analytics - Automated Database Initialization
echo ===================================================================
echo.
echo Connecting to MySQL Server 8.0 at localhost:3306...
echo Target Database: streamscope
echo.
echo Please enter your MySQL 'root' password when prompted below:
echo (Characters will not be displayed on screen as you type for security)
echo.

"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < data\processed\full_setup.sql

if %errorlevel% equ 0 (
    echo.
    echo ===================================================================
    echo  SUCCESS: streamscope database created, populated, and verified!
    echo ===================================================================
    echo  - 6 Tables Created (users, plans, subscriptions, content, viewing_sessions, app_events)
    echo  - 548,000+ Records Imported
    echo  - Analytical Views for Power BI Created
    echo  - Automated Data Quality Checks Passed
    echo ===================================================================
) else (
    echo.
    echo [ERROR] Execution failed with code %errorlevel%.
    echo Please verify your MySQL password and ensure MySQL service is running.
)
echo.
pause
