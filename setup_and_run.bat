@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"
set "OFFLINE_DIR=%PROJECT_DIR%ocr_offline_pack"

echo ========================================
echo   BossjdRPA - Setup and Run
echo ========================================
echo.

:: Step 1: Find Python 3.12 (MUST be 3.12, NOT 3.13/3.14)
echo [1/6] Detecting Python 3.12...
set "PYTHON="

:: First check the project venv (already set up)
if exist "%VENV_DIR%\Scripts\python.exe" (
    for /f "delims=" %%v in ('"%VENV_DIR%\Scripts\python.exe" --version 2^>^&1') do set "VENV_PYVER=%%v"
    echo   Existing venv: !VENV_PYVER!
    echo !VENV_PYVER! | find "3.12" >nul
    if !errorlevel!==0 (
        set "PYTHON=%VENV_DIR%\Scripts\python.exe"
        set "PYVER=!VENV_PYVER!"
        echo   Using venv Python 3.12.
        goto :skip_venv
    ) else (
        echo   Existing venv is NOT Python 3.12 - will recreate.
        rmdir /s /q "%VENV_DIR%"
    )
)

:: Check PATH for python 3.12
for %%p in (python python3) do (
    where %%p >nul 2>&1
    if !errorlevel!==0 (
        for /f "delims=" %%v in ('%%p --version 2^>^&1') do set "SYS_PYVER=%%v"
        echo !SYS_PYVER! | find "3.12" >nul
        if !errorlevel!==0 (
            set "PYTHON=%%p"
            set "PYVER=!SYS_PYVER!"
            echo   Found: %%p (!PYVER!)
            goto :found_python
        ) else (
            echo   Skipping %%p (!SYS_PYVER! - not 3.12)
        )
    )
)

:: Check common install paths for 3.12 specifically
for %%d in (
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312"
    "C:\Program Files\Python312"
    "C:\Python312"
) do (
    if exist %%d\python.exe (
        for /f "delims=" %%v in ('%%d\python.exe --version 2^>^&1') do set "PATH_PYVER=%%v"
        echo !PATH_PYVER! | find "3.12" >nul
        if !errorlevel!==0 (
            set "PYTHON=%%d\python.exe"
            set "PYVER=!PATH_PYVER!"
            echo   Found: %%d\python.exe (!PYVER!)
            goto :found_python
        )
    )
)

echo.
echo   Python 3.12 NOT found!
echo   You need Python 3.12.x (NOT 3.13, NOT 3.14).
echo   PaddlePaddle only supports Python 3.12.
echo.
echo   Download and install Python 3.12 from:
echo   https://www.python.org/downloads/
echo.
echo   IMPORTANT: Check "Add Python to PATH" during install!
pause
exit /b 1

:found_python
echo.

:: Step 2: Create virtual environment
echo [2/6] Setting up virtual environment...
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo   Creating venv with !PYVER!...
    "%PYTHON%" -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo   Failed to create venv!
        pause
        exit /b 1
    )
    echo   Venv created.
) else (
    echo   Venv already exists with correct Python version.
)

:skip_venv
:: Activate
call "%VENV_DIR%\Scripts\activate.bat"
echo.

:: Step 3: Verify Python version in venv
echo [3/6] Verifying environment...
for /f "delims=" %%v in ('python --version 2^>^&1') do set "ACTIVE_PYVER=%%v"
echo   !ACTIVE_PYVER!
echo !ACTIVE_PYVER! | find "3.12" >nul
if !errorlevel! neq 0 (
    echo   ERROR: Venv Python is not 3.12! Something went wrong.
    pause
    exit /b 1
)
echo.

:: Step 4: Install dependencies
echo [4/6] Installing dependencies...

if exist "%OFFLINE_DIR%\wheels" (
    echo   Using offline pack...
    pip install --no-index --find-links="%OFFLINE_DIR%\wheels" setuptools wheel -q 2>&1
    pip install --no-index --find-links="%OFFLINE_DIR%\wheels" pyautogui pillow numpy opencv-python requests paddlepaddle==2.6.2 "paddleocr<3.0" keyboard -q 2>&1
) else (
    echo   Downloading from internet...
    pip install pyautogui pillow numpy opencv-python requests keyboard -q 2>&1
    pip install paddlepaddle==2.6.2 -i https://pypi.tuna.tsinghua.edu.cn/simple -q 2>&1
    pip install "paddleocr<3.0" -i https://pypi.tuna.tsinghua.edu.cn/simple -q 2>&1
)

if !errorlevel! neq 0 (
    echo.
    echo   Install failed! Possible reasons:
    echo   1. Not using Python 3.12
    echo   2. Offline wheels are for a different Python version
    echo   3. Network error during online install
    pause
    exit /b 1
)
echo   Dependencies ready.
echo.

:: Step 5: Install model files (offline pack)
echo [5/6] Installing PaddleOCR models...
if exist "%OFFLINE_DIR%\models" (
    set "MODELS_DIR=%USERPROFILE%\.paddleocr\whl"
    if not exist "!MODELS_DIR!\det" (
        echo   Copying models...
        if not exist "!MODELS_DIR!" mkdir "!MODELS_DIR!"
        xcopy /E /Y "%OFFLINE_DIR%\models\*" "!MODELS_DIR!\" >nul
        echo   Models installed.
    ) else (
        echo   Models already installed.
    )
) else (
    echo   Offline pack not found. Models will download on first OCR run.
)
echo.

:: Step 6: Launch
echo [6/6] Starting RPA Console...
start "" "%VENV_DIR%\Scripts\pythonw.exe" "%PROJECT_DIR%main.py"
echo   RPA Console launched.
echo ========================================
exit
