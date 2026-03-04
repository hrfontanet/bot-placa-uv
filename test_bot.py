from bot import procesar_mensaje

def simular_chat():
    user_id = "user_test_123"
    print("--- INICIANDO SIMULACIÓN DEL BOT ---")
    print("(Escribí 'salir' para terminar o 'reinicio' para volver a empezar)\n")

    while True:
        mensaje_usuario = input("Tú: ")
        
        if mensaje_usuario.lower() == "salir":
            break
            
        # Llamada a la función principal de tu bot
        respuesta_bot = procesar_mensaje(user_id, mensaje_usuario)
        
        print(f"Bot: {respuesta_bot}\n")

if __name__ == "__main__":
    simular_chat()
