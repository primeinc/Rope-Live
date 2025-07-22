@echo off
if exist "activate.bat" (
    call activate.bat
)

call Update_Rope_Next_Local.bat

echo.
echo --------Installation Complete--------
echo.
echo You can now start the program by running the Start_Rope_Next_Local.bat or Start_Rope_Next_Dev.bat file

pause