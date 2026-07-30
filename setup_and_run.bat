@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"
set "EMBED_DIR=%PROJECT_DIR%python"
set "OFFLINE_DIR=%PROJECT_DIR%ocr_offline_pack"
set "PY_VER=3.12.10"

echo ========================================
echo   BossjdRPA - Setup and Run
echo ========================================
echo.

:: ============================================
:: Step 1: Find or install Python 3.12
:: ============================================
echo [1/7] Detecting Python 3.12...
set "PYTHON="

:: A. Check existing venv
if exist "%VENV_DIR%\Scripts\python.exe" (
    for /f "delims=" %%v in ('"%VENV_DIR%\Scripts\python.exe" --version 2^>^&1') do set "V=%%v"
    echo !V! | find "3.12" >nul
    if !errorlevel!==0 (
        set "RUN_PYTHON=%VENV_DIR%\Scripts\python.exe"
        set "RUN_PIP=%VENV_DIR%\Scripts\pip.exe"
        echo   Using existing venv ^(!V!^)
        goto :install_deps
    )
    echo   Existing venv is not 3.12 - will recreate.
    rmdir /s /q "%VENV_DIR%"
)

:: B. Check if embedded Python already set up (legacy - will redirect to full install)
if exist "%EMBED_DIR%\python.exe" (
    for /f "delims=" %%v in ('"%EMBED_DIR%\python.exe" --version 2^>^&1') do set "V=%%v"
    echo !V! | find "3.12" >nul
    if !errorlevel!==0 (
        :: Check if tkinter works (embedded Python lacks it)
        "%EMBED_DIR%\python.exe" -c "import tkinter" 2>nul
        if !errorlevel! neq 0 (
            echo   Embedded Python lacks tkinter - will download full Python instead.
            rmdir /s /q "%EMBED_DIR%"
        ) else (
            set "RUN_PYTHON=%EMBED_DIR%\python.exe"
            echo   Found embedded Python ^(!V!^)
            "%EMBED_DIR%\python.exe" -m pip --version >nul 2>&1
            if !errorlevel! neq 0 (
                echo   pip not found, downloading full Python instead.
                rmdir /s /q "%EMBED_DIR%"
            ) else (
                goto :install_deps
            )
        )
    )
)

:: C. Check PATH for python 3.12
for %%p in (python3 python) do (
    where %%p >nul 2>&1
    if !errorlevel!==0 (
        for /f "delims=" %%v in ('%%p --version 2^>^&1') do set "V=%%v"
        echo !V! | find "3.12" >nul
        if !errorlevel!==0 (
            set "SYSTEM_PYTHON=%%p"
            echo   Found on PATH: %%p ^(!V!^)
            goto :create_venv
        )
        echo   Skipping %%p ^(!V!^)
    )
)

:: D. Check common install paths
for %%d in (
    "%LOCALAPPDATA%\Programs\Python\Python312"
    "C:\Program Files\Python312"
    "C:\Python312"
) do (
    if exist "%%d\python.exe" (
        for /f "delims=" %%v in ('"%%d\python.exe" --version 2^>^&1') do set "V=%%v"
        echo !V! | find "3.12" >nul
        if !errorlevel!==0 (
            set "SYSTEM_PYTHON=%%d\python.exe"
            echo   Found: %%d\python.exe ^(!V!^)
            goto :create_venv
        )
    )
)

:: E. Not found -> auto-download and install full Python
echo   Python 3.12 not found. Downloading full installer...
echo   (about 25 MB, one-time only. This includes tkinter.)
echo.
call :download_full_python
if !errorlevel! neq 0 (
    pause
    exit /b 1
)
:: Full Python installed - use it to create venv
set "SYSTEM_PYTHON=%PYTHON%"
goto :create_venv

:: ============================================
:: Venv path (when system Python found)
:: ============================================
:create_venv
echo.
echo [2/7] Creating virtual environment...
if not exist "%VENV_DIR%\Scripts\python.exe" (
    "%SYSTEM_PYTHON%" -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo   Failed. Falling back to system Python directly.
        set "RUN_PYTHON=%SYSTEM_PYTHON%"
        set "RUN_PIP=%SYSTEM_PYTHON% -m pip"
        goto :install_deps
    )
)
set "RUN_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "RUN_PIP=%VENV_DIR%\Scripts\pip.exe"
echo   Venv ready.
goto :install_deps

:: ============================================
:: Install dependencies
:: ============================================
:install_deps
echo.
echo [3/7] Verifying Python...
for /f "delims=" %%v in ('"!RUN_PYTHON!" --version 2^>^&1') do set "ACTIVE=%%v"
echo   !ACTIVE!
echo !ACTIVE! | find "3.12" >nul
if !errorlevel! neq 0 (
    echo   ERROR: Not Python 3.12!
    pause
    exit /b 1
)

echo.
echo [4/7] Installing dependencies...
if exist "%OFFLINE_DIR%\wheels" (
    echo   Using offline pack...
    "!RUN_PYTHON!" -m pip install --no-index --find-links="%OFFLINE_DIR%\wheels" setuptools wheel -q 2>&1
    if !errorlevel! neq 0 (
        echo   Build tools install failed.
        pause & exit /b 1
    )
    "!RUN_PYTHON!" -m pip install --no-index --find-links="%OFFLINE_DIR%\wheels" pyautogui pillow numpy opencv-python requests paddlepaddle==2.6.2 "paddleocr<3.0" keyboard 2>&1
) else (
    echo   Offline pack not found. Downloading from internet...
    echo   If this fails, download ocr_offline_pack.zip from Releases.
    "!RUN_PYTHON!" -m pip install pyautogui pillow numpy opencv-python requests keyboard -i https://pypi.tuna.tsinghua.edu.cn/simple 2>&1
    if !errorlevel! neq 0 (pause & exit /b 1)
    "!RUN_PYTHON!" -m pip install paddlepaddle==2.6.2 -i https://pypi.tuna.tsinghua.edu.cn/simple 2>&1
    if !errorlevel! neq 0 (pause & exit /b 1)
    "!RUN_PYTHON!" -m pip install "paddleocr<3.0" -i https://pypi.tuna.tsinghua.edu.cn/simple 2>&1
)

if !errorlevel! neq 0 (
    echo.
    echo   ============================================
    echo   INSTALL FAILED
    echo   ============================================
    echo   Check the error messages above.
    echo   Common causes:
    echo   1. Python version mismatch - need 3.12
    echo   2. No network + no offline pack
    echo   3. Offline wheels incompatible with this Windows
    pause
    exit /b 1
)
echo   Dependencies ready.
echo.

:: ============================================
:: Models
:: ============================================
echo [5/7] PaddleOCR models...
if exist "%OFFLINE_DIR%\models" (
    set "MODELS_DIR=%USERPROFILE%\.paddleocr\whl"
    if not exist "!MODELS_DIR!\det" (
        if not exist "!MODELS_DIR!" mkdir "!MODELS_DIR!"
        xcopy /E /Y "%OFFLINE_DIR%\models\*" "!MODELS_DIR!\" >nul
        echo   Installed from offline pack.
    ) else (echo   Already installed.)
) else (echo   Will auto-download on first run.)
echo.

:: ============================================
:: Launch
:: ============================================
echo [6/7] Checking config...
if not exist "%PROJECT_DIR%rpa_config.json" (
    echo   No config file. You will need to configure API in the GUI.
)

echo [7/7] Starting...
start "" "!RUN_PYTHON!" "%PROJECT_DIR%main.py"
echo   RPA Console launched!
echo ========================================
echo.
echo   You can now close this window.
echo   Next time just double-click start_rpa.bat
pause
exit /b 0

:: ============================================
:: Subroutine: download and install full Python (includes tkinter)
:: ============================================
:download_full_python
set "INSTALLER=python-%PY_VER%-amd64.exe"
set "URL1=https://www.python.org/ftp/python/%PY_VER%/%INSTALLER%"
set "URL2=https://registry.npmmirror.com/-/binary/python/%PY_VER%/%INSTALLER%"
set "EXE=%TEMP%\%INSTALLER%"

echo   Trying: %URL1%
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri '%URL1%' -OutFile '%EXE%' -UseBasicParsing -TimeoutSec 180 } catch { exit 1 }" >nul 2>&1

if not exist "%EXE%" (
    echo   Mirror: %URL2%
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri '%URL2%' -OutFile '%EXE%' -UseBasicParsing -TimeoutSec 180 } catch { exit 1 }" >nul 2>&1
)

if not exist "%EXE%" (
    echo   DOWNLOAD FAILED. Check network.
    echo   You can manually install Python 3.12 from:
    echo   https://www.python.org/downloads/
    exit /b 1
)

for %%f in ("%EXE%") do set /a "SZ=%%~zf/1024/1024"
if !SZ! lss 15 (
    echo   Download corrupted ^(!SZ! MB^)
    del "%EXE%" 2>nul
    exit /b 1
)
echo   Downloaded !SZ! MB.

:: Silent install (no UI, user-level, add to PATH)
echo   Installing Python %PY_VER% (silent, please wait)...
"%EXE%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1
set "INSTALL_OK=!errorlevel!"

:: Wait for install to complete
timeout /t 5 /nobreak >nul

:: Find the installed Python
set "PYTHON="
for %%d in (
    "%LOCALAPPDATA%\Programs\Python\Python312"
    "%LOCALAPPDATA%\Programs\Python\Python312-32"
    "C:\Program Files\Python312"
    "%PROGRAMFILES%\Python312"
) do (
    if exist "%%d\python.exe" (
        set "PYTHON=%%d\python.exe"
        goto :full_python_found
    )
)

:: Fallback: refresh PATH and try
set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"
where python >nul 2>&1
if !errorlevel!==0 (
    for /f "delims=" %%v in ('python --version 2^>^&1') do echo   Found via PATH: %%v
    set "PYTHON=python"
    goto :full_python_found
)

echo   Install seemed to succeed but cannot find python.exe
echo   Try rebooting or installing manually.
pause
exit /b 1

:full_python_found
echo   Full Python installed.
del "%EXE%" 2>nul
exit /b 0
