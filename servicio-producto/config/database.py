from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
    "sqlite:///./db_producto.db",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autoflush = False,
    autocommit = False,
    bind=engine
)

Base = declarative_base()

def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_db = obtener_db
