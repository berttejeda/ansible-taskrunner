@echo off
:: Ghost typer
setlocal enableextensions enabledelayedexpansion

set lines=3

set "line1=tasks --help"
set "line2=."
set "line3=."

echo Enter in 'tasks --help' to display basic usage
ping localhost -n 1 >NUL

call :example
tasks --help

call :wait 1

echo Launching README in 5 seconds ...
call :wait 5
explorer C:\PROGRA~2\ANSIBL~1\README.html

goto :EOF

:wait
ping localhost -n %~1 >NUL
goto :EOF

:example
for /f %%a in ('"prompt $H&for %%b in (1) do rem"') do set "BS=%%a"
for /L %%a in (1,1,%lines%) do set num=0&set "line=!line%%a!"&call :type
goto :EOF

:type
set "letter=!line:~%num%,1!"
set "delay=%random%%random%%random%%random%%random%%random%%random%"
set "delay=%delay:~-2%"
if not "%letter%"=="" set /p "=a%bs%%letter%" <nul

:: adjust the 3 in the line below: higher is faster typing speed

for /L %%b in (1,2,%delay%) do rem
if "%letter%"=="" echo.&goto :EOF
set /a num+=1
goto :type