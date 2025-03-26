import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from subtitle_package.config import OPENAI_API_KEY
from transformers import pipeline

client = OpenAI(api_key=OPENAI_API_KEY)

class SRTTranslator:
    def __init__(self, srt_path, srt_traducido_path, idioma_destino="en",
                 num_contextos=2, max_workers=5, translate_func=None):
        """
        Inicializa el traductor de archivos SRT.
        
        Args:
            srt_path (str): Ruta del archivo SRT original.
            srt_traducido_path (str): Ruta donde se guardará el archivo traducido.
            idioma_destino (str): Código del idioma destino.
            num_contextos (int): Número de bloques de contexto a usar antes y después.
            max_workers (int): Número máximo de hilos para la concurrencia.
            translate_func (callable): Función que realiza la traducción de un texto dado.
        """
        self.srt_path = srt_path
        self.srt_traducido_path = srt_traducido_path
        self.idioma_destino = idioma_destino
        self.num_contextos = num_contextos
        self.max_workers = max_workers

        # En vez de importar la función, la recibimos como argumento
        self.translate_func = translate_func

        self.bloques = []
        self.total_bloques = 0

    def read_file(self):
        """Lee el archivo SRT y divide el contenido en bloques."""
        if not os.path.exists(self.srt_path):
            raise FileNotFoundError(f"No se encontró el archivo: {self.srt_path}")
        with open(self.srt_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        self.bloques = contenido.strip().split("\n\n")
        self.total_bloques = len(self.bloques)

    def obtener_texto_bloque(self, bloque: str) -> str:
        """Extrae el texto del bloque (a partir de la tercera línea)."""
        lineas = bloque.split("\n")
        if len(lineas) >= 3:
            return " ".join(lineas[2:]).strip()
        return ""

    def obtener_contexto_previo(self, indice: int) -> str:
        """Obtiene el contexto previo usando 'num_contextos' bloques anteriores."""
        contexto = []
        for offset in range(self.num_contextos, 0, -1):
            if indice - offset >= 0:
                contexto.append(self.obtener_texto_bloque(self.bloques[indice - offset]))
        return "\n".join(contexto)

    def obtener_contexto_siguiente(self, indice: int) -> str:
        """Obtiene el contexto siguiente usando 'num_contextos' bloques posteriores."""
        contexto = []
        for offset in range(1, self.num_contextos + 1):
            if indice + offset < self.total_bloques:
                contexto.append(self.obtener_texto_bloque(self.bloques[indice + offset]))
        return "\n".join(contexto)

    def procesar_bloque(self, indice: int) -> str:
        """
        Procesa y traduce un bloque, utilizando el contexto previo y siguiente.
        """
        bloque = self.bloques[indice]
        lineas = bloque.split("\n")
        if len(lineas) < 3:
            return bloque

        texto_actual = self.obtener_texto_bloque(bloque)
        contexto_previo = self.obtener_contexto_previo(indice)
        contexto_siguiente = self.obtener_contexto_siguiente(indice)

        print(f"[DEBUG] Traduciendo bloque {indice+1}/{self.total_bloques} con contexto ({self.num_contextos} bloques).")
        print(f"[DEBUG] Contexto previo: {contexto_previo}")
        print(f"[DEBUG] Texto a traducir: {texto_actual}")
        print(f"[DEBUG] Contexto siguiente: {contexto_siguiente}")

        # Llamamos a la función de traducción que nos pasaron en el constructor
        texto_traducido = self.translate_func(
            texto_actual,
            self.idioma_destino,
            contexto_previo=contexto_previo,
            contexto_siguiente=contexto_siguiente
        )

        # Reconstruir el bloque con las dos primeras líneas (índice y marca de tiempo) y la traducción.
        bloque_traducido = "\n".join(lineas[:2] + [texto_traducido])
        print(f"[DEBUG] Texto traducido: {bloque_traducido}\n")
        return bloque_traducido

    def translate_all(self) -> list:
        """
        Traduce todos los bloques en paralelo usando ThreadPoolExecutor.
        """
        resultados = [None] * self.total_bloques
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(self.procesar_bloque, i): i for i in range(self.total_bloques)
            }
            for future in as_completed(future_to_index):
                i = future_to_index[future]
                try:
                    resultados[i] = future.result()
                except Exception as e:
                    print(f"[ERROR] Fallo en el bloque {i+1}: {e}")
                    resultados[i] = self.bloques[i]  # fallback: usar el bloque original
        return resultados

    def write_file(self, bloques_traducidos: list):
        """Escribe el contenido traducido en el archivo de salida."""
        with open(self.srt_traducido_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(bloques_traducidos))
        print(f"[INFO] Archivo traducido guardado en: {self.srt_traducido_path}")

    def run(self):
        """
        Ejecuta el proceso completo de traducción: lectura, traducción concurrente y escritura.
        """
        self.read_file()
        bloques_traducidos = self.translate_all()
        self.write_file(bloques_traducidos)
