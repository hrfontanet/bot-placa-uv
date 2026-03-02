from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./bot.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    producto = Column(String)
    total = Column(Float)


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    precio_m2 = Column(Float)


Base.metadata.create_all(bind=engine)


def crear_productos_iniciales():
    db = SessionLocal()

    if db.query(Producto).count() == 0:
        productos = [
            Producto(nombre="Placa UV Piedra Gris", precio_m2=20000),
            Producto(nombre="Placa UV Mármol Blanco", precio_m2=24000),
            Producto(nombre="Placa UV Cemento", precio_m2=18000),
        ]

        db.add_all(productos)
        db.commit()

    db.close()


crear_productos_iniciales()
