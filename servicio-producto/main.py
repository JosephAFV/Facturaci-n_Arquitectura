from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.database import Base, engine
from router.producto_router import router as producto_router

app = FastAPI(
    title="Servicio Producto", version="1.0.0",
    description="Servicio desarrollado en Clases de Arquitectura de Software",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hoppscotch.io"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(producto_router, prefix="/api")
app.include_router(producto_router, prefix="/producto", tags=["Producto"], include_in_schema=False)

@app.get("/")
def inicio():
    return {"message": "Servicio de productos ejecutándose correctamente"}
