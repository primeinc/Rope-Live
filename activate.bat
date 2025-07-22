@echo off
REM ================================================================
REM  dynamic activate.bat  — full prompt + CUDA‑aware venv
REM  (no SETLOCAL, so everything persists in the caller’s shell)
REM ================================================================

:: ---------- Repo root & deps ----------
set "ROPE_NEXT_ROOT=%~dp0"
if "%ROPE_NEXT_ROOT:~-1%"=="\" set "ROPE_NEXT_ROOT=%ROPE_NEXT_ROOT:~0,-1%"
set "EXT_DEPENDENCIES=%ROPE_NEXT_ROOT%\ext_dependencies"

:: ---------- CUDA_PATH required ----------
if not defined CUDA_PATH (
    echo [ERROR] CUDA_PATH not set.
    echo Tip:  set CUDA_PATH="C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8"
    goto :fail
)
set "CUDA_PATH=%CUDA_PATH:"=%"

:: ---------- Detect version ----------
set "CUDA_VERSION="
echo %CUDA_PATH% | findstr /I "v12.4" >nul && set "CUDA_VERSION=cu124"
echo %CUDA_PATH% | findstr /I "v12.8" >nul && set "CUDA_VERSION=cu128"
if not defined CUDA_VERSION (
    echo [ERROR] CUDA_PATH must contain v12.4 or v12.8
    goto :fail
)

:: ---------- venv names ----------
set "VENV_DIR=venv_%CUDA_VERSION%"
set "ACTIVATE_BAT=%VENV_DIR%\Scripts\activate.bat"
set "VENV_PY=%ROPE_NEXT_ROOT%\%VENV_DIR%\Scripts\python.exe"

:: ---------- Create venv if missing ----------
if not exist "%VENV_DIR%" (
    echo [INFO] Creating %VENV_DIR%
    python -m venv "%VENV_DIR%" || goto :fail
)

:: ---------- Activate venv (inline) ----------
if not exist "%ACTIVATE_BAT%" (
    echo [ERROR] Missing %ACTIVATE_BAT%
    goto :fail
)

REM CALL keeps us in the same shell so PROMPT sticks
call "%ACTIVATE_BAT%" || goto :fail

:: ---------- Force venv python first in PATH (defensive) ----------
set "PATH=%ROPE_NEXT_ROOT%\%VENV_DIR%\Scripts;%PATH%"

:: ---------- Verify ----------
where python | find /I "%VENV_DIR%\Scripts" >nul || (
    echo [ERROR] python.exe not from venv after activation
    where python
    goto :fail
)

echo [OK] venv %CUDA_VERSION% activated.
python -m pip install --upgrade pip
echo [OK] upgraded pip.
python -m pip install wheel
echo [OK] installed wheel.

:: ---------- CUDA + FFmpeg + TensorRT prepend ----------
set "FFMPEG_PATH=%EXT_DEPENDENCIES%\ffmpeg\bin"
set "PATH=%FFMPEG_PATH%;%CUDA_PATH%\libnvvp;%CUDA_PATH%\bin;%CUDA_PATH%\lib\x64;%PATH%"

:: Add TensorRT to PATH for plugin/DLL resolution
if not defined TENSORRT_PATH set "TENSORRT_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\TensorRT\TensorRT-10.12.0.36"
set "PATH=%TENSORRT_PATH%\lib;%PATH%"
if not exist "%TENSORRT_PATH%\lib" (
	echo [ERROR] TENSORRT_PATH does not exist: %TENSORRT_PATH%
	goto :fail
)

echo [OK] venv %CUDA_VERSION% active.
goto :eof

:fail
echo.
echo [FAIL] Activation aborted.
exit /b 2
