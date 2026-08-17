from datetime import date
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DB_NAME = "facturas.db"



class FacturaCreate(BaseModel):
    numero_factura: int
    fecha: date
    cliente: str
    total: int

@app.get("/facturas")
def obtener_facturas():
    conexion = sqlite3.connect(DB_NAME)
    conexion.row_factory = (
        sqlite3.Row
    )  
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id, numero_factura, fecha, cliente, total FROM facturas ORDER BY fecha DESC;"
    )
    filas = cursor.fetchall()
    conexion.close()

    return [dict(fila) for fila in filas]

@app.get("/facturas/{id}")
def obtener_factura_por_id(id: int):
    conexion = sqlite3.connect(DB_NAME)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id, numero_factura, fecha, cliente, total FROM facturas WHERE id = ?;",
        (id,),
    )
    fila = cursor.fetchone()
    conexion.close()

    if not fila:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    return dict(fila)


@app.post("/facturas", status_code=201)
def crear_factura(factura: FacturaCreate):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO facturas (numero_factura, fecha, cliente, total)
        VALUES (?, ?, ?, ?);
    """,
        (
            factura.numero_factura,
            str(factura.fecha),
            factura.cliente,
            factura.total,
        ),
    )

    conexion.commit()
    nuevo_id = cursor.lastrowid
    conexion.close()

    return {
        "mensaje": "Factura creada con éxito",
        "id": nuevo_id,
        **factura.dict(),
    }