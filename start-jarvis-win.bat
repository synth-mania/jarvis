@echo off

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements if needed
pip install -r requirements.txt

REM Wait for 2 seconds
timeout /t 2 /nobreak >nul

REM Clear terminal
cls

REM Run the application
python -m src

REM Deactivate virtual environment when done
call venv\Scripts\deactivate.bat
