@echo off
setlocal
cd /d "%~dp0"
set "PORT=%~1"
if "%PORT%"=="" set "PORT=8138"
echo ========================================
echo   Oracle Bone and TCM Codex - Server
echo   Port: %PORT%
echo ========================================
echo.

where node >nul 2>nul
if not errorlevel 1 (
  node -e "1" >nul 2>nul
  if not errorlevel 1 (
    echo [Start] Using Node.js ...
    node serve.mjs %PORT% --host 127.0.0.1
    goto :end
  )
)

where bun >nul 2>nul
if not errorlevel 1 (
  bun -e "1" >nul 2>nul
  if not errorlevel 1 (
    echo [Start] Using Bun ...
    bun serve.mjs %PORT% --host 127.0.0.1
    goto :end
  )
)

where python >nul 2>nul
if not errorlevel 1 (
  python -c "print(1)" >nul 2>nul
  if not errorlevel 1 (
    echo [Start] Using Python ...
    python serve.py %PORT% --host 127.0.0.1
    goto :end
  )
)

echo [ERROR] Node.js / Bun / Python not found.
echo   Please install Node.js: https://nodejs.org/
pause

:end
endlocal