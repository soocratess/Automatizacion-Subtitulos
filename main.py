from subtitle_package.audio import extraer_audio
from subtitle_package.transcription import transcribir_audio
from subtitle_package.subtitles import generar_srt, traducir_srt
from subtitle_package.video import insertar_subtitulos

def menu():
    print("Bienvenido al generador de subtítulos")
    video = input("Ruta del vídeo (video.mp4): ") or "video.mp4"
    audio = input("Ruta del audio extraído (audio.wav): ") or "audio.wav"
    srt_original = input("Archivo SRT original (subtitulos.srt): ") or "subtitulos.srt"
    srt_traducido = input("Archivo SRT traducido (subtitulos_en.srt): ") or "subtitulos_en.srt"
    video_final = input("Vídeo final con subtítulos (video_con_subs.mp4): ") or "video_con_subs.mp4"
    idioma_destino = input("Idioma de destino (por defecto 'en'): ") or "en"
    return video, audio, srt_original, srt_traducido, video_final, idioma_destino

def main():
    video, audio, srt_original, srt_traducido, video_final, idioma_destino = menu()
    extraer_audio(video, audio)
    transcripcion = transcribir_audio(audio)
    generar_srt(transcripcion, srt_original)
    traducir_srt(srt_original, srt_traducido, idioma_destino)
    insertar_subtitulos(video, srt_traducido, video_final)

if __name__ == "__main__":
    main()
