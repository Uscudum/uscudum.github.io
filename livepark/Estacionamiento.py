import cv2
import numpy as np
import requests
import time

# Inicializar la captura de video desde la cámara web
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise ValueError("No se pudo acceder a la cámara web.")

# Definir la URL base de la API de ThingSpeak
url_base = "https://api.thingspeak.com/update"
api_key = "HMFN05P4RQPIR95I"

def enviar_datos_a_thingspeak(estado_binario):
    try:
        params = {
            "api_key": api_key,
            "field1": estado_binario
        }
        response = requests.get(url_base, params=params)
        if response.status_code == 200:
            print(f"Datos enviados: {estado_binario}")
        else:
            print(f"Error al enviar datos: {response.status_code}")
    except Exception as e:
        print(f"Error en la solicitud: {e}")

# Control del tiempo para el envío de datos
ultimo_envio = time.time()

# Procesar cada X frames para estado binario
procesar_cada_n_frames = 10
contador_frames = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo capturar el frame. Verifica la cámara.")
        break

    # Redimensionar el frame para reducir la carga computacional
    frame = cv2.resize(frame, (400, 300))

    # Convertir a escala de grises y aplicar binarización
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, umbral = cv2.threshold(gris, 150, 255, cv2.THRESH_BINARY_INV)

    # Obtener dimensiones del frame
    alto, ancho = frame.shape[:2]
    altura_bloque = alto // 2
    ancho_bloque = ancho // 3

    estado_binario = ""

    for i in range(2):  # Dos filas
        for j in range(3):  # Tres columnas
            x1 = j * ancho_bloque
            y1 = i * altura_bloque
            x2 = x1 + ancho_bloque
            y2 = y1 + altura_bloque

            # Extraer la región del bloque
            bloque = umbral[y1:y2, x1:x2]
            cantidad_blancos = cv2.countNonZero(bloque)
            area_bloque = (x2 - x1) * (y2 - y1)

            # Determinar si el bloque está ocupado basado en el umbral
            ocupado = cantidad_blancos > area_bloque * 0.15
            estado_binario += '1' if ocupado else '0'

            # Dibujar el rectángulo con color según el estado
            color = (0, 255, 0) if not ocupado else (0, 0, 255)  # Verde: vacío, Rojo: ocupado
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            estado = "Ocupado" if ocupado else "Vacío"
            cv2.putText(frame, estado, (x1 + 5, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # Mostrar el frame con las divisiones y los colores
    cv2.imshow('Estado del Estacionamiento', frame)

    # Enviar datos cada 2 segundos
    tiempo_actual = time.time()
    if tiempo_actual - ultimo_envio > 2:
        enviar_datos_a_thingspeak(estado_binario)
        ultimo_envio = tiempo_actual

    # Salir al presionar 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()
