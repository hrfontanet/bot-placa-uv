from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# 1. Configuración de la URL de la Base de Datos
# Prioriza la variable de entorno de Render (Supabase)
DATABASE_URL = os.getenv("DATABASE_URL")

# Si en Render pusiste postgres://, SQLAlchemy requiere que sea postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Si no hay variable (uso local), crea un archivo sqlite
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./bot.db"

# 2. Configuración del Motor (Engine)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Modelos de Datos
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

# 4. Creación de tablas
Base.metadata.create_all(bind=engine)

# 5. Carga inicial de productos (Semilla)
def semilla():
    db = SessionLocal()
    try:
        if db.query(Producto).count() == 0:
            p1 = Producto(
                nombre="Placa UV Piedra Gris", 
                precio_unidad=54300.0, 
                m2_por_unidad=2.97,
                descripcion="Placa UV rígida símil piedra gris. Se pega con silicona neutra.",
                link_url="https://wa.me/p/tu_id_1"
            )
            p2 = Producto(
                nombre="Placa UV Mármol Blanco", 
                precio_unidad=54300.0, 
                m2_por_unidad=2.97,
                descripcion="Revestimiento símil mármol blanco brillante, ideal interiores.",
                link_url="https://wa.me/p/tu_id_2"
            )
            db.add_all([p1, p2])
            db.commit()
            print("Base de datos inicializada con productos.")
    except Exception as e:
        print(f"Error en semilla: {e}")
    finally:
        db.close()

# Ejecutar la carga inicial al arrancar
semilla()
