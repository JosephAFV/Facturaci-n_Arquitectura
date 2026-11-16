from sqlalchemy import Column, Float, Integer, String

from config.database import Base

class Producto(Base):

    __tablename__ = "producto"
    codigo = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(20), nullable=False)
    descripcion = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
