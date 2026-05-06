@echo off
python "%~dp0sync-workflows.py" %*
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Python failed. Please make sure Python is installed.
)
pause
