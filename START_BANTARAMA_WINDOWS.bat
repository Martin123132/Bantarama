@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
call :check_python python
if defined PYTHON_CMD goto run_app
call :check_python py -3
if defined PYTHON_CMD goto run_app

echo Bantarama needs Python 3.10 or newer.
echo.
echo What to do:
echo   1. Go to https://www.python.org/downloads/windows/
echo   2. Download and install Python.
echo   3. Tick "Add python.exe to PATH" during install.
echo   4. Double-click START_BANTARAMA_WINDOWS.bat again.
echo.
echo Nothing has been installed or changed by Bantarama.
echo.
pause
exit /b 1

:run_app
if not defined BANTARAMA_HOME (
  if defined HOUSE_RULES_HOME (
    set "BANTARAMA_HOME=%HOUSE_RULES_HOME%"
  ) else (
    set "BANTARAMA_HOME=%~dp0data"
  )
)
echo Starting Bantarama with %PYTHON_CMD% ...
echo Your browser should open in a moment.
echo Game data folder: %BANTARAMA_HOME%
echo.
%PYTHON_CMD% -m house_rules_app.app
pause
exit /b 0

:check_python
%* -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=%*"
exit /b 0
