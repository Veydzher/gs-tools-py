@echo off
setlocal enabledelayedexpansion

rem ============================================================
rem  import.bat
rem  Drag and drop one or more .mdt/.json files onto this script.
rem  For each one, it looks for a .csv file with the SAME NAME in
rem  the SAME FOLDER and imports its strings back into that file.
rem ============================================================
set "PYTHON=python"
set "SCRIPT=%~dp0GSMdtTools.exe"

if "%~1"=="" (
    echo Drag one or more .mdt/.json files onto this script.
    echo A matching .csv with the same name must sit next to each one.
    pause
    exit /b 1
)

set ERRORS=0
set COUNT=0
set SKIPPED=0

for %%F in (%*) do (
    if /I not "%%~xF"==".csv" (
        set "CSV_FILE=%%~dpF%%~nF.csv"
        if exist "!CSV_FILE!" (
            set /a COUNT+=1
            echo.
            echo [IMPORT] !CSV_FILE! -^> %%~F
            "%PYTHON%" "%SCRIPT%" import "!CSV_FILE!" "%%~F"
            if errorlevel 1 (
                echo   ^>^> FAILED
                set /a ERRORS+=1
            )
        ) else (
            echo.
            echo [SKIP] No matching CSV for %%~F ^(expected !CSV_FILE!^)
            set /a SKIPPED+=1
        )
    )
)

echo.
echo Imported %COUNT% file^(s^), %SKIPPED% skipped, %ERRORS% error^(s^).
pause