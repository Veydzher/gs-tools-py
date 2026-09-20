@echo off
setlocal enabledelayedexpansion

rem ============================================================
rem  decode.bat
rem  Drag and drop one or more .mdt files onto this script to
rem  decode each one to a .json file.
rem ============================================================
set "PYTHON=python"
set "SCRIPT=%~dp0GSMdtTools.exe"

if "%~1"=="" (
    echo Drag one or more .mdt files onto this script to decode them.
    pause
    exit /b 1
)

set ERRORS=0
set COUNT=0

for %%F in (%*) do (
    set /a COUNT+=1
    echo.
    echo [DECODE] %%~F
    "%PYTHON%" "%SCRIPT%" decode "%%~F"
    if errorlevel 1 (
        echo   ^>^> FAILED
        set /a ERRORS+=1
    )
)

echo.
echo Processed %COUNT% file^(s^), %ERRORS% error^(s^).
pause