@echo off
:: Batch file to run the PDF extraction script

:: Navigate to the script directory (assumes the batch file is in the same folder as the Python scripts)
cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python and try again.
    pause
    exit /b
)

:: Run the main Python script
echo Running PDF Extraction...
python main.py

:: Pause at the end to keep the window open
pause
