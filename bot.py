from database import SessionLocal, Pedido

usuarios = {}

def procesar_mensaje(user_id, mensaje):

    if user_id not in usuarios:
        usuarios[user_id] = {"paso": "catalogo"}

    estado = usuarios[user_id]

    # Mostrar catálogo
    if estado["paso"] == "catalogo":

        texto = "Elegí producto:\n"
        for clave, producto in PRODUCTOS.items():
            texto += f"{clave}. {producto['nombre']} - ${producto['precio_m2']}/m²\n"

        estado["paso"] = "esperando_producto"
        return texto

    # Esperar selección de producto
    if estado["paso"] == "esperando_producto":

        if mensaje not in PRODUCTOS:
            return "Opción inválida. Elegí el número del producto."

        estado["producto"] = PRODUCTOS[mensaje]
        estado["paso"] = "esperando_m2"

        return "¿Cuántos m² necesitás cubrir?"

    # Esperar m2
    if estado["paso"] == "esperando_m2":

        try:
            m2 = float(mensaje)
        except:
            return "Ingresá un número válido de m²."

        precio_m2 = estado["producto"]["precio_m2"]
        total = m2 * precio_m2

        estado["m2"] = m2
        estado["subtotal"] = total
        estado["paso"] = "esperando_envio"

        return "¿Cómo querés recibirlo?\n1. Envío\n2. Retiro"

    # Envío o retiro
    if estado["paso"] == "esperando_envio":

        if mensaje == "1":
            costo_envio = 10000
            estado["envio"] = "Envío"
        elif mensaje == "2":
            costo_envio = 0
            estado["envio"] = "Retiro"
        else:
            return "Elegí 1 para envío o 2 para retiro."

        total_final = estado["subtotal"] + costo_envio
        estado["total_final"] = total_final
        estado["paso"] = "confirmar"

        return (
            f"\n📦 Cotización Final\n"
            f"Producto: {estado['producto']['nombre']}\n"
            f"Superficie: {estado['m2']} m²\n"
            f"Subtotal: ${estado['subtotal']}\n"
            f"{estado['envio']}: ${costo_envio}\n\n"
            f"Total Final: ${total_final}\n\n"
            "Escribí 'confirmar' o 'cancelar'."
        )

    # Confirmación
    if estado["paso"] == "confirmar":

        if mensaje.lower() == "confirmar":

            db = SessionLocal()
            nuevo_pedido = Pedido(
                user_id=user_id,
                producto=estado["producto"]["nombre"],
                total=estado["total_final"]
            )
            db.add(nuevo_pedido)
            db.commit()
            db.close()

            usuarios[user_id] = {"paso": "catalogo"}

            return "Pedido confirmado y guardado. Un asesor te contacta."

    class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    precio_m2 = Column(Float)

        else:
            usuarios[user_id] = {"paso": "catalogo"}
            return "Pedido cancelado."

    if estado["paso"] == "confirmar":
        if mensaje.lower() == "confirmar":

            db = SessionLocal()
            nuevo_pedido = Pedido(
                user_id=user_id,
                producto="Placa UV",
                total=estado["total"]
            )
            db.add(nuevo_pedido)
            db.commit()
            db.close()

            estado["paso"] = "inicio"

            return "Pedido confirmado y guardado. Un asesor te contacta."
        else:
            estado["paso"] = "inicio"
            return "Pedido cancelado."
