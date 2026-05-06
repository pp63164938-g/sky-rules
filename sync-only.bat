@echo off
set PYTHONIOENCODING=utf-8
python "%~dp0sync-workflows.py" --no-git %*
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Python failed. Please make sure Python is installed.
)
pause
