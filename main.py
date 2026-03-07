import os
import pymysql
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "domoticat_user"),
    "password": os.getenv("DB_PASSWORD"),  # ← nombre consistente
    "database": os.getenv("DB_NAME", "domoticat"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

if not DB_CONFIG["password"]:
    raise RuntimeError(
        "DB_PASSWORD no está definida en las variables de entorno.\n"
        "Por favor, configúrala en el archivo .env o exporta la variable:\n"
        "export DB_PASSWORD='tu_contraseña_segura'"
    )


# Conexión Base de Datos
def get_connection():
    """
    Establece conexión con la base de datos MySQL.

    Returns:
        tuple: (connection, cursor) para operaciones de BD

    Raises:
        RuntimeError: Si hay error de conexión
    """
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
            (codigo.upper(), descripcion),
        )
        conn.commit()
        return JSONResponse(
            status_code=201,
            content={"message": "Registro creado", "id": cursor.lastrowid},
        )
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=409, detail=f"El código '{codigo}' ya existe en {table}."
        )
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
            raise HTTPException(
                status_code=404, detail=f"id={id_} no encontrado en {table}."
            )
        cursor.execute(
            f"UPDATE {table} SET codigo = %s, descripcion = %s WHERE id = %s",
            (codigo.upper(), descripcion, id_),
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
            raise HTTPException(
                status_code=404, detail=f"id={id_} no encontrado en {table}."
            )
        cursor.execute(f"DELETE FROM {table} WHERE id = %s", (id_,))
        conn.commit()
        return JSONResponse(status_code=204, content=None)
    except HTTPException:
        raise
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: existen registros que referencian este catálogo.",
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Tabla cat_tipos_medicamento
@app.get(
    "/catalogo/tipos_medicamento",
    tags=["Catalogo - Tipos Medicamento"],
    summary="Listar tipos de medicamento",
)
async def get_cat_tipos_medicamento():
    return _cat_get("cat_tipos_medicamento")


@app.post(
    "/catalogo/tipos_medicamento",
    tags=["Catalogo - Tipos Medicamento"],
    status_code=201,
    summary="Crear tipo de medicamento",
)
async def post_cat_tipos_medicamento(codigo: str, descripcion: str | None = None):
    return _cat_post("cat_tipos_medicamento", codigo, descripcion)


@app.put(
    "/catalogo/tipos_medicamento/{id}",
    tags=["Catalogo - Tipos Medicamento"],
    summary="Actualizar tipo de medicamento",
)
async def put_cat_tipos_medicamento(
    id: int, codigo: str, descripcion: str | None = None
):
    return _cat_put("cat_tipos_medicamento", id, codigo, descripcion)


@app.delete(
    "/catalogo/tipos_medicamento/{id}",
    tags=["Catalogo - Tipos Medicamento"],
    status_code=204,
    summary="Eliminar tipo de medicamento",
)
async def del_cat_tipos_medicamento(id: int):
    return _cat_delete("cat_tipos_medicamento", id)


# Tabla cat_roles_usuario
@app.get(
    "/catalogo/roles_usuario",
    tags=["Catalogo - Roles Usuario"],
    summary="Listar roles de usuario",
)
async def get_cat_roles_usuario():
    return _cat_get("cat_roles_usuario")


@app.post(
    "/catalogo/roles_usuario",
    tags=["Catalogo - Roles Usuario"],
    status_code=201,
    summary="Crear rol de usuario",
)
async def post_cat_roles_usuario(codigo: str, descripcion: str | None = None):
    return _cat_post("cat_roles_usuario", codigo, descripcion)


@app.put(
    "/catalogo/roles_usuario/{id}",
    tags=["Catalogo - Roles Usuario"],
    summary="Actualizar rol de usuario",
)
async def put_cat_roles_usuario(id: int, codigo: str, descripcion: str | None = None):
    return _cat_put("cat_roles_usuario", id, codigo, descripcion)


@app.delete(
    "/catalogo/roles_usuario/{id}",
    tags=["Catalogo - Roles Usuario"],
    status_code=204,
    summary="Eliminar rol de usuario",
)
async def del_cat_roles_usuario(id: int):
    return _cat_delete("cat_roles_usuario", id)


# Tabla cat_sexos_gato
@app.get(
    "/catalogo/sexos_gato",
    tags=["Catalogo - Sexos Gato"],
    summary="Listar sexos de felino",
)
async def get_cat_sexos_gato():
    return _cat_get("cat_sexos_gato")


@app.post(
    "/catalogo/sexos_gato",
    tags=["Catalogo - Sexos Gato"],
    status_code=201,
    summary="Crear sexo de felino",
)
async def post_cat_sexos_gato(codigo: str, descripcion: str | None = None):
    return _cat_post("cat_sexos_gato", codigo, descripcion)


@app.put(
    "/catalogo/sexos_gato/{id}",
    tags=["Catalogo - Sexos Gato"],
    summary="Actualizar sexo de felino",
)
async def put_cat_sexos_gato(id: int, codigo: str, descripcion: str | None = None):
    return _cat_put("cat_sexos_gato", id, codigo, descripcion)


@app.delete(
    "/catalogo/sexos_gato/{id}",
    tags=["Catalogo - Sexos Gato"],
    status_code=204,
    summary="Eliminar sexo de felino",
)
async def del_cat_sexos_gato(id: int):
    return _cat_delete("cat_sexos_gato", id)


# Tabla cat_tipos_dispositivo
@app.get(
    "/catalogo/tipos_dispositivo",
    tags=["Catalogo - Tipos Dispositivo"],
    summary="Listar tipos de dispositivo",
)
async def get_cat_tipos_dispositivo():
    return _cat_get("cat_tipos_dispositivo")


@app.post(
    "/catalogo/tipos_dispositivo",
    tags=["Catalogo - Tipos Dispositivo"],
    status_code=201,
    summary="Crear tipo de dispositivo",
)
async def post_cat_tipos_dispositivo(codigo: str, descripcion: str | None = None):
    return _cat_post("cat_tipos_dispositivo", codigo, descripcion)


@app.put(
    "/catalogo/tipos_dispositivo/{id}",
    tags=["Catalogo - Tipos Dispositivo"],
    summary="Actualizar tipo de dispositivo",
)
async def put_cat_tipos_dispositivo(
    id: int, codigo: str, descripcion: str | None = None
):
    return _cat_put("cat_tipos_dispositivo", id, codigo, descripcion)


@app.delete(
    "/catalogo/tipos_dispositivo/{id}",
    tags=["Catalogo - Tipos Dispositivo"],
    status_code=204,
    summary="Eliminar tipo de dispositivo",
)
async def del_cat_tipos_dispositivo(id: int):
    return _cat_delete("cat_tipos_dispositivo", id)


# Tabla cat_tipos_consulta
@app.get(
    "/catalogo/tipos_consulta",
    tags=["Catalogo - Tipos Consulta"],
    summary="Listar tipos de consulta veterinaria",
)
async def get_cat_tipos_consulta():
    return _cat_get("cat_tipos_consulta")


@app.post(
    "/catalogo/tipos_consulta",
    tags=["Catalogo - Tipos Consulta"],
    status_code=201,
    summary="Crear tipo de consulta",
)
async def post_cat_tipos_consulta(codigo: str, descripcion: str | None = None):
    return _cat_post("cat_tipos_consulta", codigo, descripcion)


@app.put(
    "/catalogo/tipos_consulta/{id}",
    tags=["Catalogo - Tipos Consulta"],
    summary="Actualizar tipo de consulta",
)
async def put_cat_tipos_consulta(id: int, codigo: str, descripcion: str | None = None):
    return _cat_put("cat_tipos_consulta", id, codigo, descripcion)


@app.delete(
    "/catalogo/tipos_consulta/{id}",
    tags=["Catalogo - Tipos Consulta"],
    status_code=204,
    summary="Eliminar tipo de consulta",
)
async def del_cat_tipos_consulta(id: int):
    return _cat_delete("cat_tipos_consulta", id)


# Tabla cat_vias_administracion
@app.get(
    "/catalogo/vias_administracion",
    tags=["Catalogo - Vias Administracion"],
    summary="Listar vías de administración",
)
async def get_cat_vias_administracion():
    return _cat_get("cat_vias_administracion")


@app.post(
    "/catalogo/vias_administracion",
    tags=["Catalogo - Vias Administracion"],
    status_code=201,
    summary="Crear vía de administración",
)
async def post_cat_vias_administracion(codigo: str, descripcion: str | None = None):
    return _cat_post("cat_vias_administracion", codigo, descripcion)


@app.put(
    "/catalogo/vias_administracion/{id}",
    tags=["Catalogo - Vias Administracion"],
    summary="Actualizar vía de administración",
)
async def put_cat_vias_administracion(
    id: int, codigo: str, descripcion: str | None = None
):
    return _cat_put("cat_vias_administracion", id, codigo, descripcion)


@app.delete(
    "/catalogo/vias_administracion/{id}",
    tags=["Catalogo - Vias Administracion"],
    status_code=204,
    summary="Eliminar vía de administración",
)
async def del_cat_vias_administracion(id: int):
    return _cat_delete("cat_vias_administracion", id)


# Tabla cat_tipos_alerta
@app.get(
    "/catalogo/tipos_alerta",
    tags=["Catalogo - Tipos Alerta"],
    summary="Listar tipos de alerta",
)
async def get_cat_tipos_alerta():
    return _cat_get("cat_tipos_alerta")


@app.post(
    "/catalogo/tipos_alerta",
    tags=["Catalogo - Tipos Alerta"],
    status_code=201,
    summary="Crear tipo de alerta",
)
async def post_cat_tipos_alerta(codigo: str, descripcion: str | None = None):
    return _cat_post("cat_tipos_alerta", codigo, descripcion)


@app.put(
    "/catalogo/tipos_alerta/{id}",
    tags=["Catalogo - Tipos Alerta"],
    summary="Actualizar tipo de alerta",
)
async def put_cat_tipos_alerta(id: int, codigo: str, descripcion: str | None = None):
    return _cat_put("cat_tipos_alerta", id, codigo, descripcion)


@app.delete(
    "/catalogo/tipos_alerta/{id}",
    tags=["Catalogo - Tipos Alerta"],
    status_code=204,
    summary="Eliminar tipo de alerta",
)
async def del_cat_tipos_alerta(id: int):
    return _cat_delete("cat_tipos_alerta", id)


# Tabla cat_severidades_alerta
@app.get(
    "/catalogo/severidades_alerta",
    tags=["Catalogo - Severidades Alerta"],
    summary="Listar severidades de alerta",
)
async def get_cat_severidades_alerta():
    return _cat_get("cat_severidades_alerta")


@app.post(
    "/catalogo/severidades_alerta",
    tags=["Catalogo - Severidades Alerta"],
    status_code=201,
    summary="Crear severidad de alerta",
)
async def post_cat_severidades_alerta(codigo: str, descripcion: str | None = None):
    return _cat_post("cat_severidades_alerta", codigo, descripcion)


@app.put(
    "/catalogo/severidades_alerta/{id}",
    tags=["Catalogo - Severidades Alerta"],
    summary="Actualizar severidad de alerta",
)
async def put_cat_severidades_alerta(
    id: int, codigo: str, descripcion: str | None = None
):
    return _cat_put("cat_severidades_alerta", id, codigo, descripcion)


@app.delete(
    "/catalogo/severidades_alerta/{id}",
    tags=["Catalogo - Severidades Alerta"],
    status_code=204,
    summary="Eliminar severidad de alerta",
)
async def del_cat_severidades_alerta(id: int):
    return _cat_delete("cat_severidades_alerta", id)


# Tabla medicamentos


@app.get("/medicamentos", tags=["Medicamentos"], summary="Consultar medicamentos")
async def get_medicamentos():
    conn, cursor = get_connection()
    try:
        cursor.execute(
            """
            SELECT m.id_medicamento, m.nombre_comercial, m.nombre_generico,
                   m.laboratorio, c.codigo AS tipo, m.presentacion,
                   m.requiere_refrigeracion, m.esta_activo, m.fecha_creacion
            FROM   medicamentos m
            JOIN   cat_tipos_medicamento c ON c.id = m.id_tipo_medicamento
            ORDER  BY m.id_medicamento
        """
        )
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.post(
    "/medicamentos",
    tags=["Medicamentos"],
    status_code=201,
    summary="Registrar medicamento",
)
async def insert_medicamento(
    nombre_comercial: str,
    id_tipo_medicamento: int,
    laboratorio: str | None = None,
    presentacion: str | None = None,
):
    """id_tipo_medicamento: ver GET /catalogo/tipos_medicamento"""
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "INSERT INTO medicamentos (nombre_comercial, id_tipo_medicamento, laboratorio, presentacion, esta_activo) VALUES (%s,%s,%s,%s,1)",
            (nombre_comercial, id_tipo_medicamento, laboratorio, presentacion),
        )
        conn.commit()
        return JSONResponse(
            status_code=201,
            content={"message": "Medicamento registrado", "id": cursor.lastrowid},
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.put(
    "/medicamentos/{id_medicamento}",
    tags=["Medicamentos"],
    summary="Actualizar medicamento",
)
async def update_medicamento(
    id_medicamento: int, nombre_comercial: str, id_tipo_medicamento: int
):
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "SELECT id_medicamento FROM medicamentos WHERE id_medicamento=%s",
            (id_medicamento,),
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Medicamento id={id_medicamento} no encontrado.",
            )
        cursor.execute(
            "UPDATE medicamentos SET nombre_comercial=%s, id_tipo_medicamento=%s WHERE id_medicamento=%s",
            (nombre_comercial, id_tipo_medicamento, id_medicamento),
        )
        conn.commit()
        return {"message": "Medicamento actualizado"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.delete(
    "/medicamentos/{id_medicamento}",
    tags=["Medicamentos"],
    status_code=204,
    summary="Eliminar medicamento",
)
async def delete_medicamento(id_medicamento: int):
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "SELECT id_medicamento FROM medicamentos WHERE id_medicamento=%s",
            (id_medicamento,),
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Medicamento id={id_medicamento} no encontrado.",
            )
        cursor.execute(
            "DELETE FROM medicamentos WHERE id_medicamento=%s", (id_medicamento,)
        )
        conn.commit()
        return JSONResponse(status_code=204, content=None)
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Tabla usuarios
@app.get("/usuarios", tags=["Usuarios"], summary="Consultar usuarios")
async def get_usuarios():
    conn, cursor = get_connection()
    try:
        cursor.execute(
            """
            SELECT u.id_usuario, u.correo_electronico, u.nombre,
                   r.codigo AS rol, u.esta_activo, u.fecha_creacion
            FROM   usuarios u
            JOIN   cat_roles_usuario r ON r.id = u.id_rol
            ORDER  BY u.id_usuario
        """
        )
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.post("/usuarios", tags=["Usuarios"], status_code=201, summary="Registrar usuario")
async def insert_usuario(
    correo_electronico: str, nombre: str, contrasena_hash: str, id_rol: int = 1
):
    """id_rol: ver GET /catalogo/roles_usuario"""
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "INSERT INTO usuarios (correo_electronico, nombre, contrasena_hash, id_rol, esta_activo) VALUES (%s,%s,%s,%s,1)",
            (correo_electronico, nombre, contrasena_hash, id_rol),
        )
        conn.commit()
        return JSONResponse(
            status_code=201,
            content={"message": "Usuario registrado", "id": cursor.lastrowid},
        )
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=409, detail="El correo electrónico ya está registrado."
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.put("/usuarios/{id_usuario}", tags=["Usuarios"], summary="Actualizar usuario")
async def update_usuario(id_usuario: int, nombre: str, id_rol: int):
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE id_usuario=%s", (id_usuario,)
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404, detail=f"Usuario id={id_usuario} no encontrado."
            )
        cursor.execute(
            "UPDATE usuarios SET nombre=%s, id_rol=%s WHERE id_usuario=%s",
            (nombre, id_rol, id_usuario),
        )
        conn.commit()
        return {"message": "Usuario actualizado"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.delete(
    "/usuarios/{id_usuario}",
    tags=["Usuarios"],
    status_code=204,
    summary="Desactivar usuario",
)
async def delete_usuario(id_usuario: int):
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE id_usuario=%s", (id_usuario,)
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404, detail=f"Usuario id={id_usuario} no encontrado."
            )
        cursor.execute(
            "UPDATE usuarios SET esta_activo=0 WHERE id_usuario=%s", (id_usuario,)
        )
        conn.commit()
        return JSONResponse(status_code=204, content=None)
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Tabla gatos 
@app.get("/gatos", tags=["Gatos"], summary="Consultar felinos del campus")
async def get_gatos():
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            SELECT g.id_gato, g.codigo_identificacion, g.nombre,
                   s.codigo AS sexo, g.color_pelaje, g.peso_kg,
                   g.esta_esterilizado, g.id_zona_habitual,
                   g.esta_activo, g.fecha_registro
            FROM   gatos g
            JOIN   cat_sexos_gato s ON s.id = g.id_sexo
            ORDER  BY g.id_gato
        """)
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/gatos", tags=["Gatos"], status_code=201, summary="Registrar felino")
async def insert_gato(nombre: str | None = None, id_sexo: int = 3, codigo_identificacion: str | None = None, peso_kg: float = None):
    """id_sexo: ver GET /catalogo/sexos_gato (3=DESCONOCIDO)"""
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "INSERT INTO gatos (nombre, id_sexo, codigo_identificacion, peso_kg, esta_activo) VALUES (%s,%s,%s,%s,1)",
            (nombre, id_sexo, codigo_identificacion, peso_kg)
        )
        conn.commit()
        return JSONResponse(status_code=201, content={"message": "Felino registrado", "id": cursor.lastrowid})
    except Exception as e:
        conn.rollback(); raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/gatos/{id_gato}", tags=["Gatos"], summary="Actualizar felino")
async def update_gato(id_gato: int, nombre: str | None = None, peso_kg: float = None, esta_esterilizado: int = None):
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT id_gato FROM gatos WHERE id_gato=%s", (id_gato,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Gato id={id_gato} no encontrado.")
        cursor.execute("UPDATE gatos SET nombre=%s, peso_kg=%s, esta_esterilizado=%s WHERE id_gato=%s",
                       (nombre, peso_kg, esta_esterilizado, id_gato))
        conn.commit(); return {"message": "Felino actualizado"}
    except HTTPException: raise
    except Exception as e:
        conn.rollback(); raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/gatos/{id_gato}", tags=["Gatos"], status_code=204, summary="Dar de baja al felino")
async def delete_gato(id_gato: int):
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT id_gato FROM gatos WHERE id_gato=%s", (id_gato,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Gato id={id_gato} no encontrado.")
        cursor.execute("UPDATE gatos SET esta_activo=0 WHERE id_gato=%s", (id_gato,))
        conn.commit(); return JSONResponse(status_code=204, content=None)
    except HTTPException: raise
    except Exception as e:
        conn.rollback(); raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
