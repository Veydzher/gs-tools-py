@echo off
setlocal enabledelayedexpansion

rem ============================================================
rem  encode.bat
rem  Drag and drop one or more .json files onto this script to
rem  encode each one to an (unencrypted) .mdt file.
rem
rem  For an encrypted output, use encode_encrypted.bat instead.
rem ============================================================
set "PYTHON=python"
set "SCRIPT=%~dp0GSMdtTools.exe"

if "%~1"=="" (
    echo Drag one or more .json files onto this script to encode them.
    pause
    exit /b 1
)

set ERRORS=0
set COUNT=0

for %%F in (%*) do (
    set /a COUNT+=1
    echo.
    echo [ENCODE] %%~F
    "%PYTHON%" "%SCRIPT%" encode "%%~F"
    if errorlevel 1 (
        echo   ^>^> FAILED
        set /a ERRORS+=1
    )
)

echo.
echo Processed %COUNT% file^(s^), %ERRORS% error^(s^).
pause