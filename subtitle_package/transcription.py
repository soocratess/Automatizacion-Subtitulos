import whisper

# Transcribe el contenido de un archivo de audio utilizando un modelo de OpenAI Whisper.
def transcribir_audio(audio_path):
    '''
    Transcribe un archivo de audio usando el modelo Whisper de OpenAI.

    Parámetros:
        audio_path (str): Ruta al archivo de audio a transcribir.

    Retorna:
        dict: Resultado de la transcripción, incluyendo texto y segmentos temporales.
    '''
    # Cargar el modelo "base" de Whisper (puedes usar tiny, small, medium, large)
    modelo = whisper.load_model("base")

    # Transcribir el archivo de audio
    resultado = modelo.transcribe(audio_path)

    return resultado
