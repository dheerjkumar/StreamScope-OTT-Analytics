@echo off
title StreamScope - Read-Only Database & View Verification
color 0B
echo ===================================================================
echo  StreamScope OTT Analytics - Read-Only Database Verification
echo ===================================================================
echo.
echo Running read-only verification against MySQL database 'streamscope'...
echo (No tables will be dropped or modified; all queries are SELECT-only)
echo.
echo Please enter your MySQL 'root' password when prompted below:
echo.

"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p streamscope < sql\14_verify_database.sql

if errorlevel 1 goto ON_VERIFY_ERROR

echo.
echo ===================================================================
echo  VERIFICATION COMPLETE: All 6 tables and 5 views verified!
echo ===================================================================
goto VERIFY_END

:ON_VERIFY_ERROR
echo.
echo [ERROR] Verification failed with exit code %errorlevel%.
echo Please check your password and ensure MySQL server is running.

:VERIFY_END
echo.
pause
