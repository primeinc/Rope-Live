if exist "activate.bat" (
    call activate.bat
)
echo Are you sure you want to update Rope Next? (y/n)
set /p confirm=
if /i "%confirm%" neq "y" (
    echo Update cancelled.
    exit /b
)
git checkout -f development
python Rope.py
pause