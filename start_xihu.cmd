@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r xihu_map_app\requirements-lock.txt
if errorlevel 1 exit /b 1
if not exist "xihu_map_app\.env" copy "xihu_map_app\.env.example" "xihu_map_app\.env" >nul
cd xihu_map_app
"..\.venv\Scripts\python.exe" -m streamlit run xihu_map_app.py
