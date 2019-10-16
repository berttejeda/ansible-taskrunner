@echo off
mode con: cols=180 lines=40
setlocal EnableDelayedExpansion
(set \n=^
%=Do not remove this line=%
)
set ScriptPath=%~dp0
set ScriptFilePath=%~fn0
:: Doskey Alias Declarations
doskey /macrofile="%~dp0macros/default.mac"
:: Announce relevant messages
:: Read config
call :read-cfg "%~dp0cfg\default.ini"
:: Set Paths
set path=%PATH%;%~dp0;%paths%
:: Detect OS
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%version%" == "6.1" call :WINDOWS_7
if "%version%" == "6.3" call :WINDOWS_8_1
if "%version%" == "6.2" call :WINDOWS_8
if "%version%" == "10.0" call :WINDOWS_10
call :echo_banner

cd "%USERPROFILE%"
cmd /k
goto:eof

:read-cfg
FOR /F %%A IN ('TYPE "%~1" ^| FIND /v "#" ^| FIND /v "[" ') DO (
  FOR /F "Tokens=1,2 Delims==" %%B IN ("%%A") DO (set %%B=%%C)
)
goto:eof

:echo_banner
echo.
echo Ansible Taskrunner Command Console
echo.
echo If this is your first time using this tool:
echo.
echo  - Enter in the command 'start-tutorial'
echo.
goto:eof

:WINDOWS_10
echo.
echo Windows 10 Detected
call :stat-app git "https://git-scm.com/download/win"
call :stat-app python "https://www.python.org/downloads/" "(The tasks command will not work without this!)"
echo.
goto:eof

:WINDOWS_8_1
:WINDOWS_8
echo.
echo Windows 8 Detected
call :stat-app git "https://git-scm.com/download/win"
call :stat-app python "https://www.python.org/downloads/" "(The tasks command will not work without this!)"
echo.
goto:eof

:WINDOWS_7
echo.
echo Windows 7 Detected
call :stat-app git "https://git-scm.com/download/win ('Checkout as-is/Unix-style line endings')"
echo.
goto:eof

:stat-app
echo.
where "%~1" 2> nul 1> nul || echo Error: %~1 not found!\n!1. Install via %~2
echo.
goto:eof