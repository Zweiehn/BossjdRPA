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

:: Step 1: Find Python
echo [1/5] Detecting Python...
set "PYTHON="
for %%p in (python python3) do (
    where %%p >nul 2>&1
    if !errorlevel!==0 (
        for /f "delims=" %%v in ('%%p --version 2^>^&1') do set "PYVER=%%v"
        echo   Found: %%p (!PYVER!)
        set "PYTHON=%%p"
        goto :found_python
    )
)
:: Check common install paths
for %%d in (
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312"
    "C:\Program Files\Python312"
    "C:\Python312"
) do (
    if exist %%d\python.exe (
        set "PYTHON=%%d\python.exe"
        echo   Found: %%d\python.exe
        goto :found_python
    )
)
echo   Python 3.12 not found! Please install it first:
echo   https://www.python.org/downloads/
pause
exit /b 1

:found_python
echo.

:: Step 2: Create virtual environment
echo [2/5] Setting up virtual environment...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo   Creating venv...
    "%PYTHON%" -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo   Failed to create venv!
        pause
        exit /b 1
    )
    echo   Venv created.
) else (
    echo   Venv already exists.
)

:: Activate
call "%VENV_DIR%\Scripts\activate.bat"
echo.

:: Step 3: Install dependencies
echo [3/5] Installing dependencies...

if exist "%OFFLINE_DIR%\wheels" (
    echo   Using offline pack...
    pip install --no-index --find-links="%OFFLINE_DIR%\wheels" setuptools wheel -q 2>&1
    pip install --no-index --find-links="%OFFLINE_DIR%\wheels" pyautogui pillow numpy opencv-python requests paddlepaddle==2.6.2 "paddleocr<3.0" keyboard -q 2>&1
) else (
    echo   Downloading from internet (Tsinghua mirror)...
    pip install pyautogui pillow numpy opencv-python requests keyboard -q 2>&1
    pip install paddlepaddle==2.6.2 -i https://pypi.tuna.tsinghua.edu.cn/simple -q 2>&1
    pip install "paddleocr<3.0" -i https://pypi.tuna.tsinghua.edu.cn/simple -q 2>&1
)

if !errorlevel! neq 0 (
    echo   Install failed! Check error above.
    pause
    exit /b 1
)
echo   Dependencies ready.
echo.

:: Step 4: Install model files (offline pack)
echo [4/5] Installing PaddleOCR models...
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
    echo   Offline pack not found. Models will download on first OCR run (requires internet).
)
echo.

:: Step 5: Launch
echo [5/5] Starting RPA Console...
start "" "%VENV_DIR%\Scripts\pythonw.exe" "%PROJECT_DIR%main.py"
echo   RPA Console launched.
echo ========================================
exit
