@echo off
echo ================================================
echo   GENERANDO .EXE CON ENTORNO VIRTUAL LIMPIO
echo ================================================
echo.

:: Crear entorno virtual si no existe
if not exist "venv_build" (
    echo [1/5] Creando entorno virtual limpio...
    python -m venv venv_build
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause & exit /b 1
    )
    echo [OK] Entorno virtual creado
) else (
    echo [OK] Entorno virtual ya existe
)

:: Activar entorno virtual
echo.
echo [2/5] Activando entorno virtual...
call venv_build\Scripts\activate.bat

:: Instalar solo lo necesario
echo.
echo [3/5] Instalando dependencias minimas...
pip install ttkbootstrap reportlab Pillow pyinstaller --quiet
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    call deactivate
    pause & exit /b 1
)
echo [OK] Dependencias instaladas

:: Verificar carpeta assets
if not exist "assets" mkdir assets

:: Limpiar compilacion anterior
echo.
echo [4/5] Limpiando compilacion anterior...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "SistemaVentas.spec" del /q SistemaVentas.spec

:: Generar exe
echo.
echo [5/5] Compilando... (2-4 minutos)
echo.

pyinstaller --onefile --windowed ^
  --name SistemaVentas ^
  --paths . ^
  --add-data "data;data" ^
  --add-data "assets;assets" ^
  --hidden-import database.db ^
  --hidden-import controllers.controller ^
  --hidden-import views.main_window ^
  --hidden-import views.ventas_view ^
  --hidden-import views.cotizaciones_view ^
  --hidden-import views.compras_view ^
  --hidden-import views.productos_view ^
  --hidden-import views.clientes_view ^
  --hidden-import views.proveedores_view ^
  --hidden-import views.caja_view ^
  --hidden-import views.inventario_view ^
  --hidden-import views.usuarios_view ^
  --hidden-import views.catalogos_view ^
  --hidden-import views.carrito_widget ^
  --hidden-import views.base_view ^
  --hidden-import utils.pdf_export ^
  --collect-all reportlab ^
  main.py

:: Desactivar entorno
call deactivate

if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la compilacion.
    pause & exit /b 1
)

echo.
echo ================================================
echo   LISTO: dist\SistemaVentas.exe
echo ================================================
echo.
echo El .exe funciona en cualquier PC con Windows.
echo No necesita Python instalado.
echo.
echo NOTA: Pon tu logo en assets\logo.png antes
echo de distribuir el .exe.
echo ================================================
pause
