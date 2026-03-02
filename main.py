import math

# -------------------------
# DATOS
# -------------------------

productos = {
    "1": {
        "nombre": "Placa UV Piedra Gris",
        "precio": 54300,
        "cobertura": 2.97,
        "desperdicio": 0.10
    }
}

# -------------------------
# ESTADOS POR USUARIO
# -------------------------

usuarios = {}

def nuevo_estado():
    return {
        "etapa": "producto",
        "producto": None,
        "m2": None,
        "envio": None,
        "cp": None,
        "costo_envio": 0
    }

# -------------------------
# LOGICA DE NEGOCIO
# -------------------------

def calcular_producto(producto, m2):
    m2_total = m2 * (1 + producto["desperdicio"])
    unidades = math.ceil(m2_total / producto["cobertura"])
    total = unidades * producto["precio"]
    return round(m2_total,2), unidades, total

def calcular_envio(cp):
    if cp.startswith("1"):
        return 15000
    elif cp.startswith("2"):
        return 20000
    else:
        return 25000

# -------------------------
# MOTOR PRINCIPAL
# -------------------------

def procesar_mensaje(telefono, mensaje):

    if telefono not in usuarios:
        usuarios[telefono] = nuevo_estado()

    estado = usuarios[telefono]

    if estado["etapa"] == "producto":
        if mensaje in productos:
            estado["producto"] = productos[mensaje]
            estado["etapa"] = "m2"
            return "Decime los m² a cubrir."
        else:
            return "Elegí producto:\n1. Placa UV Piedra Gris"

    elif estado["etapa"] == "m2":
        try:
            estado["m2"] = float(mensaje)
            estado["etapa"] = "entrega"
            return "¿Cómo querés recibir el pedido?\n1. Envío\n2. Retiro"
        except:
            return "Enviame un número válido de m²."

    elif estado["etapa"] == "entrega":
        if mensaje == "1":
            estado["envio"] = "domicilio"
            estado["etapa"] = "cp"
            return "Ingresá tu código postal."
        elif mensaje == "2":
            estado["envio"] = "retiro"
            estado["etapa"] = "cotizacion"
        else:
            return "Elegí 1 o 2."

    if estado["etapa"] == "cp":
        estado["cp"] = mensaje
        estado["costo_envio"] = calcular_envio(mensaje)
        estado["etapa"] = "cotizacion"

    if estado["etapa"] == "cotizacion":

        m2_total, unidades, total_producto = calcular_producto(
        estado["producto"], estado["m2"]
        )

        total_final = total_producto + estado["costo_envio"]

        # Guardamos resumen en estado
        estado["resumen"] = {
          "unidades": unidades,
          "subtotal": total_producto,
          "total_final": total_final
        }

        estado["etapa"] = "confirmar"

        respuesta = f"""
    📦 Cotización Final
    Producto: {estado['producto']['nombre']}
    Superficie: {estado['m2']} m²
    Unidades: {unidades}
    Subtotal: ${total_producto:,}
    """

        if estado["envio"] == "domicilio":
            respuesta += f"Envío: ${estado['costo_envio']:,}\n"
        else:
            respuesta += "Retiro en depósito: Sin costo\n"

        respuesta += f"\nTotal Final: ${total_final:,}\n"
        respuesta += "\nEscribí 'confirmar' o 'cancelar'."

        return respuesta

    elif estado["etapa"] == "confirmar":

        if mensaje.lower() == "confirmar":

            total_final = estado["resumen"]["total_final"]

            guardar_pedido(telefono, estado, total_final)

            usuarios[telefono] = nuevo_estado()

            return "Pedido guardado correctamente. Un asesor te contacta."

        elif mensaje.lower() == "cancelar":
            usuarios[telefono] = nuevo_estado()
            return "Operación cancelada."

        else:
            return "Escribí confirmar o cancelar."

def guardar_pedido(telefono, estado, total_final):

    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO pedidos (telefono, producto, m2, envio, total, fecha)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        telefono,
        estado["producto"]["nombre"],
        estado["m2"],
        estado["envio"],
        total_final,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()
