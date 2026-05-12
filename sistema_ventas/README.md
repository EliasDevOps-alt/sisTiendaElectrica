# 🏪 SISTEMA DE VENTAS
### Sistema de gestión comercial — Desktop Python + SQLite

---

## 📋 CONTENIDO
- Gestión de Productos, Categorías y Marcas
- Gestión de Clientes y Proveedores
- Módulo de Ventas con carrito (Factura / Sin Factura)
- Módulo de Compras con actualización automática de stock
- Cotizaciones exportables a PDF y convertibles a Venta
- Inventario con valor y ganancia potencial
- Caja con movimientos automáticos y manuales
- Usuarios con roles: Administrador y Vendedor
- Exportación de Ventas y Cotizaciones a PDF

---

## ⚙️ REQUISITOS
- Windows 10/11
- Python 3.10 o superior
- Conexión a internet (solo para instalación de dependencias)

---

## 🚀 INSTALACIÓN RÁPIDA

### Opción A — Ejecutar directamente con Python
```
1. Doble clic en: INSTALAR.bat   (solo la primera vez)
2. Doble clic en: INICIAR.bat    (para abrir el sistema)
```

### Opción B — Generar el .exe
```
1. Doble clic en: INSTALAR.bat
2. Doble clic en: GENERAR_EXE.bat
3. El ejecutable queda en: dist\SistemaVentas.exe
```

### Opción C — Manual
```bash
pip install ttkbootstrap reportlab Pillow
python main.py
```

---

## 🔑 ACCESO POR DEFECTO
| Usuario | Contraseña | Rol          |
|---------|-----------|--------------|
| admin   | admin123  | Administrador|

> ⚠️ Cambia la contraseña del admin desde el menú Usuarios después del primer acceso.

---

## 📁 ESTRUCTURA DEL PROYECTO
```
sistema_ventas/
├── main.py                    ← Inicio de la aplicación + Login
├── requirements.txt           ← Dependencias Python
├── sistema_ventas.spec        ← Configuración para generar .exe
├── INSTALAR.bat               ← Instalador automático
├── INICIAR.bat                ← Lanzador del sistema
├── GENERAR_EXE.bat            ← Genera el ejecutable
│
├── database/
│   └── db.py                  ← Base de datos SQLite + triggers
│
├── controllers/
│   └── controller.py          ← Lógica de negocio completa
│
├── utils/
│   └── pdf_export.py          ← Exportación PDF con ReportLab
│
├── views/
│   ├── main_window.py         ← Ventana principal + sidebar
│   ├── base_view.py           ← Componentes UI reutilizables
│   ├── productos_view.py      ← Módulo productos
│   ├── ventas_view.py         ← Módulo ventas
│   ├── compras_view.py        ← Módulo compras
│   ├── clientes_view.py       ← Módulo clientes
│   ├── proveedores_view.py    ← Módulo proveedores
│   ├── cotizaciones_view.py   ← Módulo cotizaciones
│   ├── caja_view.py           ← Módulo caja
│   ├── inventario_view.py     ← Módulo inventario
│   ├── usuarios_view.py       ← Módulo usuarios
│   └── catalogos_view.py      ← Catálogos (categorías, marcas)
│
└── data/
    └── sistema.db             ← Base de datos (se crea automáticamente)
```

---

## 🏢 REGLAS DE NEGOCIO IMPLEMENTADAS

### Ventas
- **Sin Factura**: permite descuentos hasta el máximo del producto
- **Con Factura**: sin descuentos + IVA 13% aplicado automáticamente
- Descuento del cliente se aplica automáticamente al seleccionar producto
- Validación de stock antes de confirmar venta

### Compras
- Al registrar una compra se actualiza automáticamente:
  - Stock del producto (incrementa)
  - Precio de compra (último precio pagado)
  - Precio de venta (recalculado según % configurado)

### Roles
- **ADMIN**: acceso completo incluyendo precios de compra y ganancias
- **VENDEDOR**: solo ventas y consulta de productos (sin ver costos)

### Caja
- Las ventas generan ingresos automáticamente
- Las compras generan egresos automáticamente

---

## 📄 EXPORTACIÓN PDF
Los PDFs se guardan en el **Escritorio** del usuario con el nombre:
- `venta_000001.pdf`
- `cotizacion_000001.pdf`

Para personalizar el nombre de la empresa, editar en `utils/pdf_export.py`:
```python
EMPRESA = "MI EMPRESA"
EMPRESA_TELEFONO = "Tel: 123-456"
EMPRESA_DIRECCION = "Dirección de la empresa"
```

---

## 🔧 CONFIGURACIÓN PERSONALIZADA

### Cambiar nombre de empresa (PDF)
Editar las primeras líneas de `utils/pdf_export.py`

### Cambiar tema visual
Editar `main.py`, línea `themename`:
```python
super().__init__(themename="cosmo")
# Opciones: cosmo, flatly, litera, minty, pulse, sandstone,
#           united, yeti, morph, simplex, darkly, cyborg
```

---

## 🛠️ SOLUCIÓN DE PROBLEMAS

| Problema | Solución |
|----------|----------|
| "Python no encontrado" | Reinstalar Python marcando "Add to PATH" |
| "No module named ttkbootstrap" | Ejecutar `INSTALAR.bat` |
| La ventana no abre | Ejecutar desde CMD: `python main.py` para ver el error |
| PDF no se abre | Verificar que tienes lector de PDF instalado |

---

## 📞 SOPORTE
Sistema desarrollado con Python 3.10+ / ttkbootstrap / SQLite / ReportLab
