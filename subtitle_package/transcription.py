import io
import os
from tqdm import tqdm
from openai import OpenAI
from subtitle_package.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

class ProgressFileWrapper(io.BufferedReader):
    def __init__(self, raw, total_size, desc="Subiendo archivo"):
        super().__init__(raw)
        self.total_size = total_size
        self.progress_bar = tqdm(total=total_size, desc=desc, unit='B', unit_scale=True, unit_divisor=1024)

    def read(self, size=-1):
        chunk = super().read(size)
        self.progress_bar.update(len(chunk))
        return chunk

def transcribir_audio(audio_path):
    """
    Transcribe un archivo de audio utilizando la API de Whisper de OpenAI.

    Parámetros:
        audio_path (str): Ruta al archivo de audio a transcribir.

    Retorna:
        dict: Resultado de la transcripción proporcionado por la API.
    """
    with open(audio_path, "rb") as audio_file:
        total_size = os.path.getsize(audio_path)
        wrapped_file = ProgressFileWrapper(audio_file, total_size)
        transcript = client.audio.transcriptions.create(model="whisper-1", file=wrapped_file)
    return transcript
