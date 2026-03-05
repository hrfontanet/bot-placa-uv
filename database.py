from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL or "sqlite:///./bot.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    precio_unidad = Column(Float)
    m2_por_unidad = Column(Float, default=2.97)

def semilla():
    db = SessionLocal()
    try:
        if db.query(Producto).count() == 0:
            db.add_all([
                Producto(nombre="Placa UV Piedra Gris", precio_unidad=54300.0),
                Producto(nombre="Placa UV Mármol Blanco", precio_unidad=54300.0)
            ])
            db.commit()
    except: pass
    finally: db.close()
