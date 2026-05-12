from database.db import get_connection

def migrar_clientes_agregar_direccion():
    conn = get_connection()
    try:
        conn.execute("ALTER TABLE clientes ADD COLUMN direccion TEXT DEFAULT ''")
        conn.commit()
        print("✅ Columna 'direccion' agregada correctamente.")
    except Exception as e:
        print("⚠️ La columna ya existe o hubo un error:", e)
    finally:
        conn.close()


if __name__ == "__main__":
    migrar_clientes_agregar_direccion()