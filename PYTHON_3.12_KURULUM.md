# Python 3.12 Kurulum Rehberi

## Adım 1: İndir

https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe

Veya:
https://www.python.org/downloads/release/python-3128/
"Windows installer (64-bit)" linkine tıkla

## Adım 2: Kur

1. İndirilen .exe dosyasını çalıştır
2. **ÖNEMLİ:** "Add Python 3.12 to PATH" kutucuğunu İŞARETLE
3. "Customize installation" seç
4. Tüm optional features'ı seç
5. "Install for all users" seç (opsiyonel)
6. Install'a tıkla

## Adım 3: Doğrula

Yeni bir PowerShell/CMD aç:

```bash
py -3.12 --version
```

Çıktı: `Python 3.12.8` olmalı

## Adım 4: Kütüphaneleri Yükle

```bash
py -3.12 -m pip install opencv-python mediapipe PyQt5 numpy
```

## Adım 5: Uygulamayı Çalıştır

```bash
py -3.12 main.py
```

## Not

- Python 3.13'ü silmene gerek yok
- İki versiyon yan yana çalışabilir
- `py -3.12` ile 3.12'yi çalıştırırsın
- `python` veya `py` ile 3.13 çalışır

