import subprocess

def insertar_subtitulos(video_path, srt_path, video_con_subs):
    
    """
    Inserta (quema) subtítulos en un video utilizando ffmpeg.

    Args:
        video_path (str): Ruta del video original.
        srt_path (str): Ruta del archivo .srt que contiene los subtítulos.
        video_con_subs (str): Ruta donde se guardará el video con subtítulos incrustados.

    Raises:
        subprocess.CalledProcessError: Si el comando ffmpeg falla.
    """
    
    comando = [
        "ffmpeg",
        "-i", video_path,
        "-i", srt_path,
        "-c", "copy",
        "-c:s", "mov_text",
        video_con_subs
    ]

    
    print(f"[INFO] Insertando subtítulos en el video: {video_path}")
    subprocess.run(comando, check=True)
    print(f"[INFO] Video con subtítulos guardado en: {video_con_subs}")
