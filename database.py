from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Usamos la variable de entorno de Render
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bot.db")

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

Base.metadata.create_all(bind=engine)

def semilla():
    db = SessionLocal()
    if db.query(Producto).count() == 0:
        p1 = Producto(
            nombre="Placa UV Piedra Gris", 
            precio_unidad=54300, 
            descripcion="Rígida, se pega con silicona neutra.",
            link_url="https://wa.me/p/tu_id_1"
        )
        p2 = Producto(
            nombre="Placa UV Mármol Blanco", 
            precio_unidad=54300, 
            descripcion="Simil mármol premium, 1.22x2.44m.",
            link_url="https://wa.me/p/tu_id_2"
        )
        db.add_all([p1, p2])
        db.commit()
    db.close()

semilla()
