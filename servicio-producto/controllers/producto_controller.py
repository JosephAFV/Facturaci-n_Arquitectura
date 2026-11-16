from sqlalchemy.orm import Session

from models.producto import Producto
from schemas.producto import ProductoCreate


def obtener_producto(db: Session):
    return db.query(Producto).all()


def obtener_producto_id(db: Session, codigo: int):
    return db.get(Producto, codigo)


def crear_producto(db: Session, datos: ProductoCreate):
    producto = Producto(**datos.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


def actualizar_producto(db: Session, codigo: int, datos: ProductoCreate):
    producto = obtener_producto_id(db, codigo)
    if producto is None:
        return None

    for campo, valor in datos.model_dump().items():
        setattr(producto, campo, valor)

    db.commit()
    db.refresh(producto)
    return producto


def eliminar_producto(db: Session, codigo: int):
    producto = obtener_producto_id(db, codigo)
    if producto is None:
        return None

    db.delete(producto)
    db.commit()
    return producto
