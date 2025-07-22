@echo off

if exist "activate.bat" (
    call activate.bat
    where python
    python --version

) else (
    echo [ERROR] Missing activate.bat
    exit /b 1
)

pause
python .\tools\update_rope.py
python .\tools\download_models.py
python .\tools\detect_env.py

echo.
echo --------Update completed--------
echo.

pause
