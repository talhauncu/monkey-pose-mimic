@echo off
chcp 65001 >nul
echo.
echo =====================================
echo   Monkey Pose Mimic
echo =====================================
echo.

REM Python 3.12 var mı kontrol et
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python 3.12 bulunamadı!
    echo.
    echo MediaPipe için Python 3.12 gereklidir.
    echo.
    echo Kurulum:
    echo 1. İndir: https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe
    echo 2. Kur ^(Add to PATH işaretle^)
    echo 3. Bu dosyayı tekrar çalıştır
    echo.
    pause
    exit /b 1
)

echo [OK] Python 3.12 bulundu
py -3.12 --version
echo.

REM MediaPipe kontrol
py -3.12 -c "import mediapipe" >nul 2>&1
if errorlevel 1 (
    echo [UYARI] MediaPipe yüklü değil, yükleniyor...
    echo.
    py -3.12 -m pip install opencv-python mediapipe PyQt5 numpy
    echo.
    if errorlevel 1 (
        echo [HATA] Kütüphaneler yüklenemedi!
        pause
        exit /b 1
    )
    echo [OK] Kütüphaneler yüklendi
    echo.
)

echo [BAŞLATILIYOR] Uygulama başlatılıyor...
echo.
py -3.12 main.py

if errorlevel 1 (
    echo.
    echo [HATA] Uygulama hatayla kapandı!
    pause
)

