from .SRTTranslator import SRTTranslator

# IMPORTS PARA GPT
from openai import OpenAI
from subtitle_package.config import OPENAI_API_KEY

# Instancia del cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def convertir_tiempo(segundos):
    """
    Convierte un tiempo en segundos al formato HH:MM:SS,mmm usado en archivos SRT.
    """
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    seg = int(segundos % 60)
    miliseg = int((segundos - int(segundos)) * 1000)
    return f"{horas:02}:{minutos:02}:{seg:02},{miliseg:03}"

def generar_srt(transcripcion, srt_path):
    """
    Genera un archivo SRT a partir de una transcripción.
    """
    print(f"[INFO] Generando archivo SRT en: {srt_path}")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segmento in enumerate(transcripcion['segments'], start=1):
            inicio = convertir_tiempo(segmento['start'])
            fin = convertir_tiempo(segmento['end'])
            texto = segmento['text'].strip()
            f.write(f"{i}\n{inicio} --> {fin}\n{texto}\n\n")

def traducir_texto_gpt(texto, idioma_destino="en", contexto_previo="", contexto_siguiente=""):
    """
    Traduce un texto usando GPT (ChatCompletion) incluyendo contexto.
    
    Args:
        texto (str): Texto a traducir.
        idioma_destino (str): Código del idioma destino (ej: "en", "fr", etc.).
        contexto_previo (str): Texto que antecede al texto principal para dar contexto.
        contexto_siguiente (str): Texto que sigue al texto principal para dar contexto.
    
    Returns:
        str: Solo la traducción del "Texto a traducir".
    """
    prompt = (
        f"TRADUCE AL IDIOMA '{idioma_destino.upper()}' SOLO EL SIGUIENTE TEXTO. "
        "UTILIZA EL CONTEXTO PREVIO Y EL CONTEXTO SIGUIENTE PARA MEJORAR LA PRECISIÓN DE LA TRADUCCIÓN, "
        "Y CORRIGE CUALQUIER ERROR ORTOGRÁFICO. NO INCLUYAS NINGÚN CONTENIDO ADICIONAL.\n\n"
        "=== CONTEXTO PREVIO ===\n"
        f"{contexto_previo}\n\n"
        "=== TEXTO A TRADUCIR ===\n"
        f"{texto}\n\n"
        "=== CONTEXTO SIGUIENTE ===\n"
        f"{contexto_siguiente}\n\n"
        "RESPONDE CON ÚNICAMENTE LA TRADUCCIÓN EXACTA Y CORREGIDA."
    )

    respuesta = client.chat.completions.create(
        model="gpt-3.5-turbo",  # O "gpt-4", "gpt-4o", etc.
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un traductor profesional. Tu tarea es traducir exactamente el texto indicado, "
                    "utilizando el contexto proporcionado para obtener la mejor traducción posible. "
                    "No añadas ningún comentario ni explicación. Responde únicamente con la traducción."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    texto_traducido = respuesta.choices[0].message.content.strip()
    return texto_traducido

def traducir_srt(srt_path, srt_traducido_path, idioma_destino="en", num_contextos=2, max_workers=5):
    """
    Traduce un archivo SRT completo utilizando la clase SRTTranslator.
    """
    translator = SRTTranslator(
        srt_path=srt_path,
        srt_traducido_path=srt_traducido_path,
        idioma_destino=idioma_destino,
        num_contextos=num_contextos,
        max_workers=max_workers,
        # Pasamos la función de traducción
        translate_func=traducir_texto_gpt
    )
    translator.run()
