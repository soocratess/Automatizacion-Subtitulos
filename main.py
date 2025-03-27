from subtitle_package.audio import extraer_audio
from subtitle_package.transcription import transcribir_audio
from subtitle_package.subtitles import generar_srt, traducir_srt
from subtitle_package.video import insertar_subtitulos

def menu():
    print("Bienvenido al generador de subtítulos")
    print("La ruta por defecto de los archivos es 'media/'")

    video_input = input("Ruta del vídeo (video.mp4): ")
    audio_input = input("Ruta del audio extraído (audio.wav): ")
    srt_original_input = input("Archivo SRT original (subtitulos.srt): ")
    srt_traducido_input = input("Archivo SRT traducido (subtitulos_en.srt): ")
    video_final_input = input("Vídeo final con subtítulos (video_con_subs.mp4): ")
    idioma_destino = input("Idioma de destino (por defecto 'en'): ") or "en"

    video = "media/" + (video_input or "video.mp4")
    audio = "media/" + (audio_input or "audio.wav")
    srt_original = "media/" + (srt_original_input or "subtitulos.srt")
    srt_traducido = "media/" + (srt_traducido_input or "subtitulos_en.srt")
    video_final = "media/" + (video_final_input or "video_con_subs.mp4")

    return video, audio, srt_original, srt_traducido, video_final, idioma_destino

def main():
    video, audio, srt_original, srt_traducido, video_final, idioma_destino = menu()
#    extraer_audio(video, audio)
    transcripcion = transcribir_audio("media/chunk_0.wav", chunk_length_ms=60000, max_workers=5)
    generar_srt(transcripcion, srt_original)
    traducir_srt(srt_original, srt_traducido, idioma_destino, num_contextos=3, max_workers=5)
    insertar_subtitulos(video, srt_traducido, video_final)

if __name__ == "__main__":
    main()
