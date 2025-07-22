@echo off
REM --------------------------------------------
REM Rope-cu128 Launcher
REM - Activates Python venv
REM - Sets environment for CUDA 12.8
REM - Links TensorRT engine dir for cu128
REM - Runs Rope.py
REM --------------------------------------------

REM Activate environment and set up base variables
call activate.bat

REM Override to explicitly use CUDA 12.8 for runtime
set "CUDA_PATH=%CUDA_PATH_V12_8%"

REM Remove old symlink (if exists)
if exist "tensorrt-engines" (
    rmdir "tensorrt-engines"
)

REM Ensure versioned engine folder exists
if not exist "tensorrt-engines-cu128" (
    mkdir "tensorrt-engines-cu128"
)

REM Link: tensorrt-engines → tensorrt-engines-cu128
mklink /D "tensorrt-engines" "tensorrt-engines-cu128"

REM Execute Rope
python Rope.py

pause
