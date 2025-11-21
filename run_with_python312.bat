@echo off
echo Python 3.12 ile calistiriliyor...
echo.

REM Python 3.12 var mi kontrol et
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python 3.12 bulunamadi!
    echo.
    echo Lutfen once Python 3.12 yukleyin:
    echo https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe
    echo.
    echo Veya PYTHON_3.12_KURULUM.md dosyasina bakin
    pause
    exit /b 1
)

echo Python 3.12 bulundu!
echo.

REM Kutuphaneler yuklu mu kontrol et
py -3.12 -c "import mediapipe" >nul 2>&1
if errorlevel 1 (
    echo MediaPipe yukleniyor...
    py -3.12 -m pip install opencv-python mediapipe PyQt5 numpy
    echo.
)

echo Uygulama baslatiliyor...
py -3.12 main.py

pause

