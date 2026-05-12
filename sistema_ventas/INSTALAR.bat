@echo off
echo ================================================
echo   INSTALADOR - SISTEMA DE VENTAS
echo ================================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.
echo Instalando dependencias...
pip install ttkbootstrap reportlab Pillow --quiet

if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas correctamente
echo.
echo ================================================
echo   INSTALACION COMPLETADA
echo   Ejecuta: python main.py
echo   O doble clic en: INICIAR.bat
echo ================================================
pause
