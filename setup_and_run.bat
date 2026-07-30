@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"
set "EMBED_DIR=%PROJECT_DIR%python"
set "OFFLINE_DIR=%PROJECT_DIR%ocr_offline_pack"
set "PY_VER=3.12.10"
set "PY_URL=https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%-embed-amd64.zip"

echo ========================================
echo   BossjdRPA - Setup and Run
echo ========================================
echo.

:: Step 1: Find or install Python 3.12
echo [1/7] Detecting Python 3.12...
set "PYTHON="

:: Check existing venv
if exist "%VENV_DIR%\Scripts\python.exe" (
    for /f "delims=" %%v in ('"%VENV_DIR%\Scripts\python.exe" --version 2^>^&1') do set "V=%%v"
    echo !V! | find "3.12" >nul
    if !errorlevel!==0 (
        set "PYTHON=%VENV_DIR%\Scripts\python.exe"
        echo   Using existing venv (!V!^)
        goto :skip_venv
    ) else (
        echo   Existing venv is not 3.12 - will recreate.
        rmdir /s /q "%VENV_DIR%"
    )
)

:: Check PATH
for %%p in (python3 python) do (
    where %%p >nul 2>&1
    if !errorlevel!==0 (
        for /f "delims=" %%v in ('%%p --version 2^>^&1') do set "V=%%v"
        echo !V! | find "3.12" >nul
        if !errorlevel!==0 (
            set "PYTHON=%%p"
            echo   Found: %%p (!V!^)
            goto :found_python
        )
        echo   Skipping %%p (!V!^)
    )
)

:: Check common paths
for %%d in (
    "%LOCALAPPDATA%\Programs\Python\Python312"
    "C:\Program Files\Python312"
    "C:\Python312"
    "%LOCALAPPDATA%\Programs\Python\Python312"
) do (
    if exist %%d\python.exe (
        for /f "delims=" %%v in ('%%d\python.exe --version 2^>^&1') do set "V=%%v"
        echo !V! | find "3.12" >nul
        if !errorlevel!==0 (
            set "PYTHON=%%d\python.exe"
            echo   Found: %%d\python.exe (!V!^)
            goto :found_python
        )
    )
)

:: Not found -> auto-download embedded Python 3.12
echo   Python 3.12 not found. Auto-installing embedded Python...
echo   Downloading Python %PY_VER% (about 10 MB)...

:: Try main URL + mirror
set "DL_OK=0"
for %%u in ("%PY_URL%" "https://registry.npmmirror.com/-/binary/python/%PY_VER%/python-%PY_VER%-embed-amd64.zip") do (
    if !DL_OK!==0 (
        powershell -Command "try { Invoke-WebRequest -Uri %%u -OutFile '%TEMP%\python-embed.zip' -UseBasicParsing -TimeoutSec 120 } catch {}"
        if exist "%TEMP%\python-embed.zip" (
            for %%f in ("%TEMP%\python-embed.zip") do set /a "SZ=%%~zf/1024/1024"
            if !SZ! geq 5 (set "DL_OK=1" & echo   Downloaded !SZ! MB)
        )
    )
)

if !DL_OK!==0 (
    echo   Download failed. Please install Python 3.12 manually:
    echo   https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Extract embedded Python
echo   Extracting...
if exist "%EMBED_DIR%" rmdir /s /q "%EMBED_DIR%"
mkdir "%EMBED_DIR%"
powershell -Command "Expand-Archive -Path '%TEMP%\python-embed.zip' -DestinationPath '%EMBED_DIR%' -Force"
del "%TEMP%\python-embed.zip"

:: Configure embedded Python (enable pip + site-packages)
echo   Configuring...
echo python312.zip>. "%EMBED_DIR%\python312._pth"
echo .>> "%EMBED_DIR%\python312._pth"
echo import site>> "%EMBED_DIR%\python312._pth"
echo Lib\site-packages>> "%EMBED_DIR%\python312._pth"
mkdir "%EMBED_DIR%\Lib\site-packages" 2>nul

:: Install pip into embedded Python
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%TEMP%\get-pip.py' -UseBasicParsing"
"%EMBED_DIR%\python.exe" "%TEMP%\get-pip.py" --no-setuptools --no-wheel -q 2>&1
if !errorlevel! neq 0 (
    echo   Failed to install pip!
    pause
    exit /b 1
)

set "PYTHON=%EMBED_DIR%\python.exe"
echo   Embedded Python %PY_VER% ready.
goto :found_python

:found_python
echo.

:: Step 2: Create venv
echo [2/7] Creating virtual environment...
if not exist "%VENV_DIR%\Scripts\python.exe" (
    "%PYTHON%" -m venv "%VENV_DIR%" 2>&1
    if !errorlevel! neq 0 (
        echo   venv failed, using Python directly...
        set "PYTHON=%PYTHON%"
        goto :skip_venv
    )
    echo   venv created.
)

:skip_venv
:: Prefer venv python, fallback to direct python
if exist "%VENV_DIR%\Scripts\python.exe" (
    set "RUN_PYTHON=%VENV_DIR%\Scripts\python.exe"
    set "RUN_PIP=%VENV_DIR%\Scripts\pip.exe"
) else (
    set "RUN_PYTHON=%PYTHON%"
    set "RUN_PIP=%PYTHON% -m pip"
)
echo   Using: !RUN_PYTHON!

:: Step 3: Verify 3.12
echo [3/7] Verifying Python version...
for /f "delims=" %%v in ('"!RUN_PYTHON!" --version 2^>^&1') do set "ACTIVE=%%v"
echo   !ACTIVE!
echo !ACTIVE! | find "3.12" >nul
if !errorlevel! neq 0 (
    echo   ERROR: Not Python 3.12!
    pause
    exit /b 1
)
echo.

:: Step 4: Install dependencies
echo [4/7] Installing dependencies...
if exist "%OFFLINE_DIR%\wheels" (
    echo   Using offline pack...
    "!RUN_PIP!" install --no-index --find-links="%OFFLINE_DIR%\wheels" setuptools wheel -q 2>&1
    "!RUN_PIP!" install --no-index --find-links="%OFFLINE_DIR%\wheels" pyautogui pillow numpy opencv-python requests paddlepaddle==2.6.2 "paddleocr<3.0" keyboard 2>&1
) else (
    echo   Using Tsinghua mirror...
    "!RUN_PIP!" install pyautogui pillow numpy opencv-python requests keyboard -i https://pypi.tuna.tsinghua.edu.cn/simple 2>&1
    "!RUN_PIP!" install paddlepaddle==2.6.2 -i https://pypi.tuna.tsinghua.edu.cn/simple 2>&1
    "!RUN_PIP!" install "paddleocr<3.0" -i https://pypi.tuna.tsinghua.edu.cn/simple 2>&1
)

if !errorlevel! neq 0 (
    echo   Install failed - check errors above.
    pause
    exit /b 1
)
echo   Dependencies ready.
echo.

:: Step 5: Models
echo [5/7] Installing PaddleOCR models...
if exist "%OFFLINE_DIR%\models" (
    set "MODELS_DIR=%USERPROFILE%\.paddleocr\whl"
    if not exist "!MODELS_DIR!\det" (
        if not exist "!MODELS_DIR!" mkdir "!MODELS_DIR!"
        xcopy /E /Y "%OFFLINE_DIR%\models\*" "!MODELS_DIR!\" >nul
        echo   Models installed.
    ) else (echo   Models already installed.)
) else (echo   Will download on first run.)
echo.

:: Step 6: Config check
echo [6/7] Checking configuration...
if not exist "%PROJECT_DIR%rpa_config.json" (
    echo   No rpa_config.json found - will create on first save.
) else (
    echo   rpa_config.json found.
)
echo.

:: Step 7: Launch
echo [7/7] Starting RPA Console...
start "" "!RUN_PYTHON!" "%PROJECT_DIR%main.py"
echo   Launched!
echo ========================================
exit
