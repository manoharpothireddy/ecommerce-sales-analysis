@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: E-Commerce Sales & Customer Behavior Analysis
:: Setup Script for Windows
:: ============================================================

echo.
echo ============================================================
echo   E-Commerce Sales ^& Customer Behavior Analysis
echo   Environment Setup
echo ============================================================
echo.

:: --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo [INFO]  Python version detected: %PYTHON_VERSION%

:: --- Create virtual environment ---
if exist venv\ (
    echo [INFO]  Virtual environment 'venv' already exists. Skipping creation.
) else (
    echo [INFO]  Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK]    Virtual environment created at .\venv
)

:: --- Activate virtual environment ---
echo [INFO]  Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo [OK]    Virtual environment activated.

:: --- Upgrade pip ---
echo [INFO]  Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK]    pip upgraded.

:: --- Install requirements ---
echo [INFO]  Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK]    All dependencies installed successfully.

:: --- Register Jupyter kernel ---
echo [INFO]  Registering Jupyter kernel...
python -m ipykernel install --user --name ecommerce-analysis --display-name "Python (ecommerce-analysis)"
echo [OK]    Jupyter kernel registered as 'ecommerce-analysis'.

echo.
echo ============================================================
echo   Setup complete!
echo.
echo   To activate the environment in future sessions:
echo     venv\Scripts\activate
echo.
echo   To launch Jupyter Notebook:
echo     jupyter notebook
echo.
echo   To launch Jupyter Lab:
echo     jupyter lab
echo ============================================================
echo.
pause
