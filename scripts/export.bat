@echo off
setlocal enabledelayedexpansion

rem ============================================================
rem  export.bat
rem  Drag and drop one or more .mdt/.json files onto this script
rem  to export each one's strings to a .csv file.
rem ============================================================
set "PYTHON=python"
set "SCRIPT=%~dp0GSMdtTools.exe"

if "%~1"=="" (
    echo Drag one or more .mdt/.json files onto this script to export them.
    pause
    exit /b 1
)

set ERRORS=0
set COUNT=0

for %%F in (%*) do (
    set /a COUNT+=1
    echo.
    echo [EXPORT] %%~F
    "%PYTHON%" "%SCRIPT%" export "%%~F"
    if errorlevel 1 (
        echo   ^>^> FAILED
        set /a ERRORS+=1
    )
)

echo.
echo Processed %COUNT% file^(s^), %ERRORS% error^(s^).
pause