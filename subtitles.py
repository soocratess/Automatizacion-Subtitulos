import subprocess
import whisper
from transformers import pipeline

# Paso 1: Extraer audio del vídeo usando ffmpeg.
def extraer_audio(video_path, audio_path):
    comando = [
        "ffmpeg", "-i", video_path,
        "-vn",                    # Sin video
        "-acodec", "pcm_s16le",   # Codec de audio sin compresión
        "-ar", "44100",           # Frecuencia de muestreo
        "-ac", "2",               # Dos canales (estéreo)
        audio_path
    ]
    subprocess.run(comando, check=True)

# Paso 2: Transcribir el audio usando Whisper.
def transcribir_audio(audio_path):
    modelo = whisper.load_model("base")  # Puedes elegir otro modelo según tus necesidades.
    resultado = modelo.transcribe(audio_path)
    return resultado

# Función para convertir segundos a formato SRT (HH:MM:SS,mmm).
def convertir_tiempo(segundos):
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    seg = int(segundos % 60)
    miliseg = int((segundos - int(segundos)) * 1000)
    return f"{horas:02}:{minutos:02}:{seg:02},{miliseg:03}"

# Paso 3: Generar un archivo SRT a partir de la transcripción.
def generar_srt(transcripcion, srt_path):
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segmento in enumerate(transcripcion['segments'], start=1):
            inicio = convertir_tiempo(segmento['start'])
            fin = convertir_tiempo(segmento['end'])
            texto = segmento['text'].strip()
            f.write(f"{i}\n{inicio} --> {fin}\n{texto}\n\n")

# Paso 4: Traducir el texto (subtítulos) usando un modelo de Hugging Face.
def traducir_texto(texto, idioma_destino="en"):
    # Utiliza un modelo de traducción de Helsinki-NLP para traducir de español a inglés (o a otro idioma)
    traductor = pipeline("translation", model=f"Helsinki-NLP/opus-mt-es-{idioma_destino}")
    resultado = traductor(texto)
    return resultado[0]['translation_text']

def traducir_srt(srt_path, srt_traducido_path, idioma_destino="en"):
    with open(srt_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Separa los bloques de subtítulos (cada bloque está separado por una línea vacía)
    bloques = contenido.strip().split("\n\n")
    bloques_traducidos = []
    
    for bloque in bloques:
        lineas = bloque.split("\n")
        if len(lineas) >= 3:
            # Las dos primeras líneas son el número y el intervalo de tiempo.
            texto_original = " ".join(lineas[2:])
            texto_traducido = traducir_texto(texto_original, idioma_destino)
            bloque_traducido = "\n".join(lineas[:2] + [texto_traducido])
            bloques_traducidos.append(bloque_traducido)
        else:
            bloques_traducidos.append(bloque)
    
    with open(srt_traducido_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(bloques_traducidos))

# Paso 5 (opcional): Insertar (quemar) subtítulos en el vídeo final usando ffmpeg.
def insertar_subtitulos(video_path, srt_path, video_con_subs):
    comando = [
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_path}",
        "-c:a", "copy",
        video_con_subs
    ]
    subprocess.run(comando, check=True)

def menu():
    print("Bienvenido al generador de subtítulos")
    print("La carpeta 'media' es el directorio por defecto para los archivos.")
    print()
    video = "media/" + (input("Ingrese la ruta del vídeo (video.mp4): ") or "video.mp4")
    audio = "media/" + (input("Ingrese la ruta para guardar el audio extraído (audio.wav): ") or "audio.wav")
    srt_original = "media/" + (input("Ingrese la ruta para guardar el archivo SRT original (subtitulos.srt): ") or "subtitulos.srt")
    srt_traducido = "media/" + (input("Ingrese la ruta para guardar el archivo SRT traducido (subtitulos_en.srt): ") or "subtitulos_en.srt")
    video_final = "media/" + (input("Ingrese la ruta para guardar el vídeo final con subtítulos (video_con_subs.mp4): ") or "video_con_subs.mp4")
    idioma_destino = input("Ingrese el idioma de destino para la traducción (por defecto 'en'): ") or "en"
    return video, audio, srt_original, srt_traducido, video_final, idioma_destino

def main():
    video, audio, srt_original, srt_traducido, video_final, idioma_destino = menu()

    # Extraer el audio del vídeo.
    extraer_audio(video, audio)
        
    # Transcribir el audio usando Whisper.
    transcripcion = transcribir_audio(audio)
        
    # Generar el archivo SRT a partir de la transcripción.
    generar_srt(transcripcion, srt_original)
        
    # Traducir el archivo SRT al idioma deseado.
    traducir_srt(srt_original, srt_traducido, idioma_destino)
        
    # (Opcional) Insertar los subtítulos traducidos en el vídeo final.
    insertar_subtitulos(video, srt_traducido, video_final)

if __name__ == "__main__":
    main()
