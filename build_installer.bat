@echo off
setlocal enabledelayedexpansion

:: Enable command echoing for debugging
@echo on

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

:: Change to the script directory
cd /d "%SCRIPT_DIR%"

echo Script directory: %SCRIPT_DIR%
echo Current directory: %CD%

echo Building VinnyPix Typing Tools Installer...
echo =======================================
echo Current directory: %CD%

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.10.0 or later and try again.
    pause
    exit /b 1
)

:: Check if required packages are installed
echo Checking for required Python packages...
python -m pip install --upgrade pip

:: Create a simple requirements.txt without version constraints
if not exist "requirements.txt" (
    echo Creating requirements.txt...
    (
        echo pyautogui
        echo opencv-python
        echo pytesseract
        echo keyboard
        echo pywin32
        echo numpy
        echo pillow
    ) > requirements.txt
)

:: Install required packages
echo Installing required packages...
python -m pip install -r requirements.txt

:: Check if PIL/Pillow is installed (needed for icon generation)
python -c "import PIL" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing Pillow for icon generation...
    python -m pip install pillow
)

:: Create internal directory if it doesn't exist
if not exist "internal" mkdir internal

:: Create an empty icon file if it doesn't exist
if not exist "internal\icon.ico" (
    echo. 2>nul > "internal\icon.ico"
)

:: Build the executable
echo Building the executable...
python -c "import sys; print('Python version:', sys.version)"
python -c "import pyautogui, cv2, pytesseract, keyboard, win32gui, win32con, win32api; print('All imports successful')"

:: Run the build script with error handling
python build.py
if %ERRORLEVEL% NEQ 0 (
    echo Error: Build failed with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo =======================================
    echo Error building the application. Check the output above for details.
    pause
    exit /b 1
)

:: Check if NSIS is installed
where makensis >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: NSIS is not installed or not in PATH.
    echo The executable has been built, but you need NSIS to create the installer.
    echo Please install NSIS from https://nsis.sourceforge.io/Download
    echo and add it to your system PATH.
    echo.
    pause
    exit /b 0
)

:: Create the installer
echo Creating the installer...
if exist "installer.nsi" (
    makensis installer.nsi
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo =======================================
        echo Build completed successfully!
    echo Installer created: VinnyPixTypingTools_Setup.exe
    echo =======================================
) else (
    echo.
    echo =======================================
    echo Error creating the installer.
    echo Please check the output for errors.
    echo =======================================
)

pause
