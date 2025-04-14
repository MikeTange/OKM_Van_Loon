@echo off
setlocal

REM Check if Python is installed
where python >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python not found. Installing...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    setx PATH "%ProgramFiles%\Python312\Scripts;%ProgramFiles%\Python312\"
) else (
    echo Python is already installed.
)

REM Install Python packages
echo Installing required packages...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Setup complete. You can now double-click the executable.
pause