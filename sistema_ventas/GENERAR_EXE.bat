@echo off
echo ================================================
echo   GENERANDO EJECUTABLE .EXE
echo ================================================
echo.

pip install pyinstaller --quiet
echo [OK] PyInstaller listo
echo.
echo Compilando... (puede tardar 2-5 minutos)
echo.

pyinstaller sistema_ventas.spec --clean --noconfirm

if errorlevel 1 (
    echo [ERROR] Fallo la compilacion.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   EXE GENERADO EN: dist\SistemaVentas.exe
echo ================================================
pause
