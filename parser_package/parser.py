#!/usr/bin/env python3
import sys
import re
import math

def srt_time_to_seconds(t):
    """
    Convierte una marca de tiempo SRT (ejemplo "00:36:26,798") a segundos (float).
    """
    parts = t.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    sec, millis = parts[2].split(',')
    seconds = int(sec)
    millis = int(millis)
    return hours * 3600 + minutes * 60 + seconds + millis / 1000

def seconds_to_srt_time(s):
    """
    Convierte un número de segundos a una cadena en formato SRT (HH:MM:SS,mmm).
    """
    hours = int(s // 3600)
    minutes = int((s % 3600) // 60)
    seconds = int(s % 60)
    millis = int(round((s - int(s)) * 1000))
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

def parse_srt_file(filename):
    """
    Lee el archivo SRT y devuelve una lista de bloques con índice, tiempos y texto.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    # Separa bloques por dos saltos de línea
    blocks = content.split("\n\n")
    parsed = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) >= 3:
            index = lines[0].strip()
            time_line = lines[1].strip()
            # Une el resto de líneas en un solo texto
            text = " ".join(lines[2:]).strip()
            # Extraer tiempos (formato: "00:36:26,798 --> 00:36:33,159")
            time_parts = time_line.split(" --> ")
            if len(time_parts) != 2:
                continue
            start_time = time_parts[0].strip()
            end_time = time_parts[1].strip()
            parsed.append({
                'index': int(index),
                'start': start_time,
                'end': end_time,
                'text': text
            })
    return parsed

def process_block(block, max_length=140):
    """
    Si el texto del bloque supera max_length caracteres, lo divide en dos
    usando como punto de corte la palabra que ocupa la posición media.
    
    Además, divide el intervalo de tiempo original en dos, usando la mitad
    (promedio de inicio y fin) como nueva marca de tiempo.
    """
    if len(block['text']) <= max_length:
        return [block]

    words = block['text'].split()
    half_index = len(words) // 2
    first_text = " ".join(words[:half_index])
    second_text = " ".join(words[half_index:])

    start_sec = srt_time_to_seconds(block['start'])
    end_sec = srt_time_to_seconds(block['end'])
    mid_sec = (start_sec + end_sec) / 2

    block1 = {
        'index': None,  # se asignará después
        'start': block['start'],
        'end': seconds_to_srt_time(mid_sec),
        'text': first_text
    }
    block2 = {
        'index': None,
        'start': seconds_to_srt_time(mid_sec),
        'end': block['end'],
        'text': second_text
    }
    return [block1, block2]

def process_blocks(blocks, max_length=140):
    """
    Recorre la lista de bloques y divide aquellos cuyo texto supere max_length.
    Luego, renumera todos los bloques secuencialmente.
    """
    new_blocks = []
    for block in blocks:
        new_blocks.extend(process_block(block, max_length))
    new_blocks.sort(key=lambda b: srt_time_to_seconds(b['start']))
    for i, block in enumerate(new_blocks, start=1):
        block['index'] = i
    return new_blocks

def generate_srt(blocks):
    """
    Genera el contenido SRT a partir de la lista de bloques.
    """
    output = []
    for block in blocks:
        output.append(str(block['index']))
        output.append(f"{block['start']} --> {block['end']}")
        output.append(block['text'])
        output.append("")  # línea en blanco
    return "\n".join(output)

def parse(input_file, output_file, max_length=140):
    blocks = parse_srt_file(input_file)
    processed_blocks = process_blocks(blocks, max_length)
    srt_content = generate_srt(processed_blocks)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    print(f"[INFO] Archivo SRT generado en: {output_file}")
