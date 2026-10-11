@echo off
chcp 65001 > nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [KURULUM HATASI] .venv bulunamadi. README.md dosyasindaki kurulum adimlarini uygulayin.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" baslat.py
if errorlevel 1 (
  echo.
  echo [BASLATMA HATASI] Uygulama kapandi. Terminaldeki hata ayrintilarini kontrol edin.
  pause
)
