@echo off
echo Setting up Network Traffic Management System...

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM Create .env file from example
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
    echo Please edit .env with your configuration
)

echo Setup complete!
echo Activate virtual environment with: venv\Scripts\activate.bat
echo Run the system with: python main.py
