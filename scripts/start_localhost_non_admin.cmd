@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_localhost_non_admin.ps1" %*
endlocal
