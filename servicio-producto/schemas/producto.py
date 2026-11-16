from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated


class ProductoCreate(BaseModel):
    nombre: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
    descripcion: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    precio: float = Field(ge=0, allow_inf_nan=False)
    stock: int = Field(ge=0)


class ProductoResponse(ProductoCreate):
    codigo: int

    model_config = ConfigDict(from_attributes=True)
