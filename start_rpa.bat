@echo off
set "PROJECT_DIR=%~dp0"

:: Check: system pythonw (most common case)
where pythonw >nul 2>&1
if %errorlevel%==0 (
    pythonw -c "import tkinter; import paddleocr" >nul 2>&1
    if %errorlevel%==0 (
        start "" pythonw "%PROJECT_DIR%main.py"
        exit
    )
)

:: Check: venv (set up by setup_and_run.bat on other machines)
if exist "%PROJECT_DIR%venv\Scripts\pythonw.exe" (
    "%PROJECT_DIR%venv\Scripts\pythonw.exe" -c "import tkinter; import paddleocr" >nul 2>&1
    if %errorlevel%==0 (
        start "" "%PROJECT_DIR%venv\Scripts\pythonw.exe" "%PROJECT_DIR%main.py"
        exit
    )
)

:: 3. Cannot start - need to run setup
echo ========================================
echo   Cannot start: environment not ready.
echo ========================================
echo.
echo   Run setup_and_run.bat first.
echo   It only needs to run ONCE.
echo.
pause
