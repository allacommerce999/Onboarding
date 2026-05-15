@echo off
setlocal
cd /d "%~dp0\.."
set "PYTHONPATH=%CD%\src"
python -m onboarding_app.server
endlocal
