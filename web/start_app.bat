@echo off

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Attempting to install Python...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python-3.11.7.exe'}"
    echo Download complete.

    echo Installing Python...
    start /wait python-3.11.7.exe /quiet InstallAllUsers=1 PrependPath=1

    echo Python installed successfully.
) else (
    echo Python version detected:
    python --version
)

REM Create a virtual environment
echo Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate

REM Install required libraries from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Run the Python application
echo Starting the application...
python main.py

REM Pause the script when done
pause
