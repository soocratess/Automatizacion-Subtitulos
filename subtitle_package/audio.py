import subprocess

def extraer_audio(video_path, audio_path):
    """
    Extrae el audio de un archivo de video utilizando ffmpeg y lo guarda como archivo WAV.

    Args:
        video_path (str): Ruta del archivo de video de entrada.
        audio_path (str): Ruta donde se guardará el archivo de audio extraído (formato WAV).

    Raises:
        subprocess.CalledProcessError: Si el comando ffmpeg falla.
    """
    # Comando para extraer solo el audio (-vn), sin comprimir (pcm_s16le), estéreo, 44100 Hz
    comando = [
        "ffmpeg", "-i", video_path,
        "-vn",                     # Elimina el video
        "-acodec", "pcm_s16le",    # Formato WAV (sin compresión)
        "-ar", "44100",            # Frecuencia de muestreo
        "-ac", "2",                # Audio estéreo
        audio_path
    ]

    print(f"[INFO] Extrayendo audio desde: {video_path}")
    subprocess.run(comando, check=True)
    print(f"[INFO] Audio extraído y guardado en: {audio_path}")
