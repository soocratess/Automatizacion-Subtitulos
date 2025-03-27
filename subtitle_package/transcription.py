import os
import re
import math
from tqdm import tqdm
from pydub import AudioSegment
from pydub.utils import make_chunks
from openai import OpenAI
from subtitle_package.config import OPENAI_API_KEY
from concurrent.futures import ThreadPoolExecutor, as_completed

client = OpenAI(api_key=OPENAI_API_KEY)

def split_audio(audio_path, chunk_length_ms):
    """
    Divide un archivo de audio en fragmentos de duración especificada (en milisegundos).
    """
    audio = AudioSegment.from_file(audio_path)
    chunks = make_chunks(audio, chunk_length_ms)
    return chunks

def save_chunks(chunks, output_dir):
    """
    Guarda cada fragmento en un archivo WAV y devuelve la lista de rutas.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_filename = os.path.join(output_dir, f"chunk_{i}.wav")
        chunk.export(chunk_filename, format="wav")
        chunk_files.append(chunk_filename)
    return chunk_files

def srt_time_to_seconds(srt_time):
    """
    Convierte una marca de tiempo SRT (ejemplo "00:00:55,200") a segundos (float).
    """
    hours, minutes, sec_millis = srt_time.split(':')
    seconds, millis = sec_millis.split(',')
    total = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000.0
    return total

def seconds_to_srt_time(seconds):
    """
    Convierte un número de segundos a una cadena en formato SRT (HH:MM:SS,mmm).
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def parse_srt(srt_text):
    """
    Parsea un texto en formato SRT y devuelve una lista de segmentos.
    Cada segmento es un diccionario con 'index', 'start', 'end' y 'text'.
    """
    segments = []
    pattern = re.compile(r'(\d+)\s+([\d:,]+)\s+-->\s+([\d:,]+)\s+(.*?)(?=\n\n|\Z)', re.DOTALL)
    matches = pattern.findall(srt_text)
    for match in matches:
        index = int(match[0])
        start = srt_time_to_seconds(match[1])
        end = srt_time_to_seconds(match[2])
        text = match[3].strip().replace('\n', ' ')
        segments.append({
            'index': index,
            'start': start,
            'end': end,
            'text': text
        })
    return segments

def generate_srt(segments):
    """
    Genera un string en formato SRT a partir de una lista de segmentos.
    Los segmentos se renumeran secuencialmente.
    """
    srt_lines = []
    for i, seg in enumerate(segments, start=1):
        srt_lines.append(str(i))
        srt_lines.append(f"{seconds_to_srt_time(seg['start'])} --> {seconds_to_srt_time(seg['end'])}")
        srt_lines.append(seg['text'])
        srt_lines.append("")  # línea en blanco entre segmentos
    return "\n".join(srt_lines)

def transcribe_chunk(index, chunk_file, chunk_length_ms):
    """
    Transcribe un fragmento individual utilizando el formato "srt".
    Ajusta el offset en función del índice del fragmento.
    """
    with open(chunk_file, "rb") as audio_file:
        srt_text = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="srt"
        )
    segments = parse_srt(srt_text)
    # Calcular el offset en segundos para este fragmento
    chunk_offset = index * (chunk_length_ms / 1000.0)
    for seg in segments:
        seg['start'] += chunk_offset
        seg['end'] += chunk_offset
    return segments

def transcribe_chunks(chunk_files, chunk_length_ms, max_workers):
    """
    Transcribe cada fragmento en paralelo usando un ThreadPoolExecutor.
    """
    all_segments = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(transcribe_chunk, i, chunk_file, chunk_length_ms): i 
                   for i, chunk_file in enumerate(chunk_files)}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Transcribiendo fragmentos"):
            segments = future.result()
            all_segments.extend(segments)
    return all_segments

def transcribir_audio(audio_path, chunk_length_ms=60000, max_workers=5):
    """
    Devuelve un diccionario con la transcripción completa y la lista de segmentos.
    """
    print("[INFO] Dividiendo el audio en fragmentos...")
    chunks = split_audio(audio_path, chunk_length_ms)
    print(f"[INFO] El audio se ha dividido en {len(chunks)} fragmentos.")

    print("[INFO] Guardando fragmentos en disco...")
    chunk_files = save_chunks(chunks, "chunks")

    print("[INFO] Transcribiendo cada fragmento en paralelo...")
    segments = transcribe_chunks(chunk_files, chunk_length_ms, max_workers)
    segments.sort(key=lambda seg: seg['start'])
    full_text = " ".join(seg["text"] for seg in segments)
    return {"text": full_text.strip(), "segments": segments}

# --- Nuevas funciones para dividir segmentos largos ---

def split_segment(segment, max_duration=5):
    """
    Si la duración del segmento es mayor a max_duration (segundos), lo divide en partes iguales.
    Reparte el texto en partes iguales (por palabras) para cada subsegmento.
    """
    duration = segment['end'] - segment['start']
    if duration <= max_duration:
        return [segment]
    num_subsegments = math.ceil(duration / max_duration)
    words = segment['text'].split()
    words_per_segment = math.ceil(len(words) / num_subsegments)
    subsegments = []
    for i in range(num_subsegments):
        new_start = segment['start'] + (duration / num_subsegments) * i
        new_end = segment['start'] + (duration / num_subsegments) * (i + 1)
        sub_text_words = words[i * words_per_segment:(i + 1) * words_per_segment]
        sub_text = " ".join(sub_text_words)
        subsegments.append({
            'index': None,  # se asignará luego
            'start': new_start,
            'end': new_end,
            'text': sub_text
        })
    return subsegments

def split_long_segments(segments, max_duration=5):
    """
    Recorre la lista de segmentos y divide aquellos cuya duración supere max_duration.
    """
    new_segments = []
    for seg in segments:
        new_segments.extend(split_segment(seg, max_duration))
    new_segments.sort(key=lambda x: x['start'])
    # Reasigna los índices secuencialmente
    for i, seg in enumerate(new_segments, start=1):
        seg['index'] = i
    return new_segments
