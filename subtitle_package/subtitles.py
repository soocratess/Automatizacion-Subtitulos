from transformers import pipeline
import os
import openai

def convertir_tiempo(segundos):
    """
    Convierte un tiempo en segundos al formato HH:MM:SS,mmm usado en archivos SRT.

    Args:
        segundos (float): Tiempo en segundos.

    Returns:
        str: Tiempo formateado como string.
    """
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    seg = int(segundos % 60)
    miliseg = int((segundos - int(segundos)) * 1000)
    return f"{horas:02}:{minutos:02}:{seg:02},{miliseg:03}"

def generar_srt(transcripcion, srt_path):
    """
    Genera un archivo SRT a partir de una transcripción.

    Args:
        transcripcion (dict): Resultado del modelo Whisper con segmentos de texto.
        srt_path (str): Ruta donde se guardará el archivo SRT generado.
    """
    print(f"[INFO] Generando archivo SRT en: {srt_path}")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segmento in enumerate(transcripcion['segments'], start=1):
            inicio = convertir_tiempo(segmento['start'])
            fin = convertir_tiempo(segmento['end'])
            texto = segmento['text'].strip()
            f.write(f"{i}\n{inicio} --> {fin}\n{texto}\n\n")

def traducir_texto(texto, idioma_destino="en"):
    """
    Traduce un bloque de texto desde español a otro idioma usando un modelo Hugging Face.

    Args:
        texto (str): Texto a traducir.
        idioma_destino (str): Código del idioma destino (por defecto "en").

    Returns:
        str: Texto traducido.
    """
    traductor = pipeline("translation", model=f"Helsinki-NLP/opus-mt-es-{idioma_destino}")
    resultado = traductor(texto)
    return resultado[0]['translation_text']

def traducir_texto_gpt(texto, idioma_destino="en"):
    """
    Traduce un texto usando GPT (ChatCompletion).
    
    Args:
        texto (str): Texto a traducir.
        idioma_destino (str): Código del idioma destino. Ej: "en", "fr", "de", etc.
    
    Returns:
        str: Texto traducido.
    """
    # Creamos el prompt de traducción
    prompt = (
        f"Por favor, traduce el siguiente texto al idioma '{idioma_destino}':\n\n"
        f"{texto}"
    )

    # Llamada a la API de OpenAI
    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # O "gpt-4" si tienes acceso
        messages=[
            {"role": "system", "content": "Eres un traductor experto."},
            {"role": "user", "content": prompt}
        ],
        temperature=0  # Pon temperatura 0 para minimizar variaciones en la traducción
    )

    # Extraemos el texto traducido
    texto_traducido = respuesta.choices[0].message["content"].strip()
    return texto_traducido


def traducir_srt(srt_path, srt_traducido_path, idioma_destino="en"):
    """
    Traduce un archivo SRT completo línea por línea, conservando el formato de subtítulo.

    Args:
        srt_path (str): Ruta del archivo SRT original.
        srt_traducido_path (str): Ruta donde se guardará el archivo traducido.
        idioma_destino (str): Código del idioma destino (por defecto "en").
    """
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"No se encontró el archivo: {srt_path}")

    print(f"[INFO] Traduciendo subtítulos desde {srt_path} a {idioma_destino}...")

    with open(srt_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    bloques = contenido.strip().split("\n\n")
    bloques_traducidos = []

    for bloque in bloques:
        lineas = bloque.split("\n")
        if len(lineas) >= 3:
            texto_original = " ".join(lineas[2:])
            texto_traducido = traducir_texto_gpt(texto_original, idioma_destino)
            bloque_traducido = "\n".join(lineas[:2] + [texto_traducido])
            bloques_traducidos.append(bloque_traducido)
        else:
            bloques_traducidos.append(bloque)

    with open(srt_traducido_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(bloques_traducidos))

    print(f"[INFO] Archivo traducido guardado en: {srt_traducido_path}")
