from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmarker, declarative_base

engine = create_engine("sqlite:///./db_producto.db")