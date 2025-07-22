if exist "activate.bat" (
    call activate.bat
)
echo Are you sure you want to update Rope Next? (y/n)
set /p confirm=
if /i "%confirm%" neq "y" (
    echo Update cancelled.
    exit /b
)
git checkout -f main
git reset --hard origin/main
git pull origin main
python .\tools\download_models.py
python .\tools\update_rope.py

echo.
echo --------Update completed--------
echo.

pause