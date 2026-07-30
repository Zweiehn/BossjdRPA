@echo off
set "PROJECT_DIR=%~dp0"

:: Check: venv
if exist "%PROJECT_DIR%venv\Scripts\pythonw.exe" (
    start "" "%PROJECT_DIR%venv\Scripts\pythonw.exe" "%PROJECT_DIR%main.py"
    exit
)

:: Check: embedded python
if exist "%PROJECT_DIR%python\pythonw.exe" (
    start "" "%PROJECT_DIR%python\pythonw.exe" "%PROJECT_DIR%main.py"
    exit
)

:: Check: system python
where pythonw >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw "%PROJECT_DIR%main.py"
    exit
)

:: Nothing found
echo ========================================
echo   Cannot start - No Python found!
echo ========================================
echo.
echo   Run setup_and_run.bat first to auto-install Python.
echo   It only needs to run once.
echo.
pause
