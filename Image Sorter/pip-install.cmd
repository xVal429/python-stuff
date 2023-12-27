@echo off
setlocal

echo This script will install the following Python packages:^
- pillow^
- send2trash
echo.
set /p "response=Do you want to continue (Y/N)? "
if /i "%response%" neq "Y" (
    echo Installation cancelled by user.
    exit /b
)

pip show pillow | findstr /B /I "Name: pillow" >nul
if errorlevel 1 (
    pip install pillow
    echo Pillow installed successfully.
) else (
    echo Pillow is already installed.
)

pip show send2trash | findstr /B /I "Name: send2trash" >nul
if errorlevel 1 (
    pip install send2trash
    echo Send2Trash installed successfully.
) else (
    echo Send2Trash is already installed.
)

pause

endlocal