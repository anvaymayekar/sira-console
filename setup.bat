@echo off
echo ================================
echo SIRA Console Setup
echo ================================
echo.

REM Check Python
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
venv\Scripts\python -m pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To run SIRA Console:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo 2. Run the application:
echo    python main.py
echo.
pause