@echo off
setlocal

:: Get full path of this script's directory
set "SCRIPT_DIR=%~dp0"

:: Remove trailing backslash
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Get parent directory
for %%A in ("%SCRIPT_DIR%") do set "PARENT_DIR=%%~dpA"

:: Get the name of the current directory (for use as the module name)
for %%B in ("%SCRIPT_DIR%") do set "BASE_MODULE=%%~nxB"

:: Run python in a subshell after cd-ing to parent
cmd /c "cd /d "%PARENT_DIR%" && py -OO -m "%BASE_MODULE%" %*"

endlocal
