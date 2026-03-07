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

