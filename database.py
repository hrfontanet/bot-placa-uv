from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./bot.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    precio_unidad = Column(Float)
    m2_por_unidad = Column(Float, default=2.97)
    descripcion = Column(String)
    link_url = Column(String)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    detalle = Column(String)
    total = Column(Float)

def semilla():
    db = SessionLocal()
    try:
        if db.query(Producto).count() == 0:
            p1 = Producto(nombre="Placa UV Piedra Gris", precio_unidad=54300.0, m2_por_unidad=2.97)
            p2 = Producto(nombre="Placa UV Mármol Blanco", precio_unidad=54300.0, m2_por_unidad=2.97)
            db.add_all([p1, p2])
            db.commit()
    except Exception as e:
        print(f"Error en semilla: {e}")
    finally:
        db.close()
