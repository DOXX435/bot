@echo off
title Batch Menu Example
cls

:MENU
echo ==========================
echo       MAIN MENU
echo ==========================
echo 1. Option 1 - Test
echo 2. Option 2 - Test
echo 3. Option 3 - Test
echo 4. Exit
echo ==========================
set /p choice="Please select an option (1-4): "

if "%choice%"=="1" goto OPTION1
if "%choice%"=="2" goto OPTION2
if "%choice%"=="3" goto OPTION3
if "%choice%"=="4" exit

goto MENU

:OPTION1
cls
echo You selected Option 1 - Test
echo.
echo This is where the code for Option 1 goes.
pause
goto MENU

:OPTION2
cls
echo You selected Option 2 - Test
echo.
echo This is where the code for Option 2 goes.
pause
goto MENU

:OPTION3
cls
echo You selected Option 3 - Test
echo.
echo This is where the code for Option 3 goes.
pause
goto MENU
