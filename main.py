import os
import pymysql
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv("DB_HOST", "localhost"), 
    'port': int(os.getenv("DB_PORT", 3306)),
    'user': os.getenv("DB_USER", "domoticat_user"),
    'password': os.getenv("DB_PASSWORD"),  # ← nombre consistente
    'database': os.getenv("DB_NAME", "domoticat"),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

if not DB_CONFIG["password"]:
    raise RuntimeError(
        "DB_PASSWORD no está definida en las variables de entorno.\n"
        "Por favor, configúrala en el archivo .env o exporta la variable:\n"
        "export DB_PASSWORD='tu_contraseña_segura'"
    )

# Conexión Base de Datos
def get_connection():
    conn = pymysql.connect(**DB_CONFIG)
    return conn, conn.cursor()

# Instacia de objeto FastAPI 
app = FastAPI(
    title="Domoticat API",
    description=(
        "**API REST** del sistema Domoticat — gestión de la comunidad felina "
        "de la Universidad de Cundinamarca."
    ),
    version="1.0.0",
)

@app.get("/", tags=["Sistema"])
async def root():
    return {"message": "Domoticat API v1.0 funcionando correctamente."}

# Endpoints reutilizables para todos los catálogos

def _cat_get(table: str):
    conn, cursor = get_connection()
    try:
        cursor.execute(f"SELECT id, codigo, descripcion FROM {table} ORDER BY id")
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


def _cat_post(table: str, codigo: str, descripcion: str | None = None):
    conn, cursor = get_connection()
    try:
        cursor.execute(
            f"INSERT INTO {table} (codigo, descripcion) VALUES (%s, %s)",
            (codigo.upper(), descripcion)
        )
        conn.commit()
        return JSONResponse(status_code=201, content={"message": "Registro creado", "id": cursor.lastrowid})
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=409, detail=f"El código '{codigo}' ya existe en {table}.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


def _cat_put(table: str, id_: int, codigo: str, descripcion: str | None = None):
    conn, cursor = get_connection()
    try:
        cursor.execute(f"SELECT id FROM {table} WHERE id = %s", (id_,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"id={id_} no encontrado en {table}.")
        cursor.execute(
            f"UPDATE {table} SET codigo = %s, descripcion = %s WHERE id = %s",
            (codigo.upper(), descripcion, id_)
        )
        conn.commit()
        return {"message": "Registro actualizado"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


def _cat_delete(table: str, id_: int):
    conn, cursor = get_connection()
    try:
        cursor.execute(f"SELECT id FROM {table} WHERE id = %s", (id_,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"id={id_} no encontrado en {table}.")
        cursor.execute(f"DELETE FROM {table} WHERE id = %s", (id_,))
        conn.commit()
        return JSONResponse(status_code=204, content=None)
    except HTTPException:
        raise
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: existen registros que referencian este catálogo.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()