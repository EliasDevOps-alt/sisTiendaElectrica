# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('data', 'data'), ('assets', 'assets')]
binaries = []
hiddenimports = ['database.db', 'controllers.controller', 'views.main_window', 'views.ventas_view', 'views.cotizaciones_view', 'views.compras_view', 'views.productos_view', 'views.clientes_view', 'views.proveedores_view', 'views.caja_view', 'views.inventario_view', 'views.usuarios_view', 'views.catalogos_view', 'views.carrito_widget', 'views.base_view', 'utils.pdf_export']
tmp_ret = collect_all('reportlab')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SistemaVentas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
