@echo off
set "PROJECT_DIR=%~dp0"

:: Priority: venv > embedded python > system pythonw
if exist "%PROJECT_DIR%venv\Scripts\pythonw.exe" (
    start "" "%PROJECT_DIR%venv\Scripts\pythonw.exe" "%PROJECT_DIR%main.py"
) else if exist "%PROJECT_DIR%python\pythonw.exe" (
    start "" "%PROJECT_DIR%python\pythonw.exe" "%PROJECT_DIR%main.py"
) else (
    start "" pythonw "%PROJECT_DIR%main.py"
)
