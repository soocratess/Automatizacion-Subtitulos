# Generador de Subtítulos y Traducción

Este proyecto es una herramienta en Python que extrae el audio de un vídeo, lo transcribe utilizando el modelo Whisper, genera un archivo de subtítulos en formato SRT y, a continuación, traduce dichos subtítulos a otro idioma (por defecto, inglés) usando la API de OpenAI. Finalmente, se pueden incrustar (quemar) los subtítulos traducidos en el vídeo final mediante ffmpeg.

## Tabla de contenidos

- [Generador de Subtítulos y Traducción](#generador-de-subtítulos-y-traducción)
  - [Tabla de contenidos](#tabla-de-contenidos)
  - [Características](#características)
  - [Estructura del Proyecto](#estructura-del-proyecto)
  - [Requisitos](#requisitos)
  - [Instalación y Configuración](#instalación-y-configuración)
    - [1. Clonar el Repositorio](#1-clonar-el-repositorio)
    - [2. Crear y Activar el Entorno Virtual](#2-crear-y-activar-el-entorno-virtual)
    - [3. Instalar Dependencias](#3-instalar-dependencias)
    - [4. Configurar la API de OpenAI](#4-configurar-la-api-de-openai)
  - [Uso](#uso)
  - [Notas adicionales](#notas-adicionales)
  - [Licencia](#licencia)

## Características

- **Extracción de audio:** Utiliza `ffmpeg` para extraer el audio de un vídeo.
- **Transcripción:** Emplea el modelo Whisper para convertir el audio en texto.
- **Generación de subtítulos:** Crea un archivo SRT a partir de la transcripción, con marcas de tiempo.
- **Traducción contextual:** Traduce los subtítulos utilizando la API de OpenAI (por ejemplo, GPT-3.5-turbo), teniendo en cuenta el contexto completo para obtener una traducción de alta calidad.
- **Inserción de subtítulos:** Permite quemar los subtítulos traducidos en el vídeo final.

## Estructura del Proyecto

La estructura de archivos del proyecto es la siguiente:

```
.
├── config.py
├── media
│   ├── audio.wav
│   ├── subtitulos_en.srt
│   ├── subtitulos.srt
│   ├── test.mp4
│   └── video_con_subs.mp4
├── README.md
├── requirements.txt
├── subtitles.py
└── venv
    ├── bin
    ├── include
    ├── lib
    ├── lib64 -> lib
    ├── pyvenv.cfg
    └── share
```

- **config.py:** Se encarga de cargar la configuración sensible (como la API key de OpenAI) desde variables de entorno.
- **media:** Carpeta donde se almacenan los archivos multimedia generados o de prueba.
- **subtitles.py:** Script principal que orquesta la extracción, transcripción, generación, traducción e inserción de subtítulos.
- **requirements.txt:** Lista de dependencias necesarias para el proyecto.
- **venv:** Entorno virtual de Python (se recomienda crear y gestionar este entorno de forma local).

## Requisitos

- **Python 3.12** (u otra versión compatible)
- **ffmpeg** instalado en el sistema (disponible en la mayoría de distribuciones Linux, macOS y Windows)
- Acceso a la API de OpenAI (con tu API key)
- Conexión a Internet para realizar las traducciones con la API

## Instalación y Configuración

### 1. Clonar el Repositorio

Clona el proyecto en tu ordenador:

```bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
```

### 2. Crear y Activar el Entorno Virtual

Crea un entorno virtual (si no existe ya la carpeta `venv`):

```bash
python3 -m venv venv
```

Actívalo:

- **En Linux o macOS (bash/fish/zsh):**

  ```bash
  source venv/bin/activate
  ```

- **En Windows (cmd):**

  ```cmd
  venv\Scripts\activate.bat
  ```

- **En Windows (PowerShell):**

  ```powershell
  venv\Scripts\Activate.ps1
  ```

### 3. Instalar Dependencias

Instala las dependencias necesarias con pip:

```bash
pip install -r requirements.txt
```

### 4. Configurar la API de OpenAI

Crea un archivo `.env` en la raíz del proyecto (este archivo NO debe subirse a GitHub). Añade el siguiente contenido:

```dotenv
OPENAI_API_KEY=tu_api_key_aqui
```

El archivo `.gitignore` ya debe incluir `.env` para evitar que se comparta accidentalmente.

## Uso

Para ejecutar el script, asegúrate de que el entorno virtual está activado y lanza el script desde la terminal:

```bash
python subtitles.py
```

Se te solicitarán las rutas de los archivos y el idioma de destino para la traducción. Por defecto, el script utilizará:

- **Vídeo de entrada:** `video.mp4` (o `media/test.mp4` si así lo configuras)
- **Audio extraído:** `audio.wav`
- **Subtítulos originales:** `subtitulos.srt`
- **Subtítulos traducidos:** `subtitulos_en.srt`
- **Vídeo final con subtítulos:** `video_con_subs.mp4`

Ajusta las rutas según tus necesidades. Todos los archivos generados se pueden guardar en la carpeta `media`.

## Notas adicionales

- **Uso de la API de OpenAI:** El script utiliza un prompt que tiene en cuenta el contexto completo para obtener una traducción de alta calidad. Puedes modificar el prompt en la función `traducir_texto` según tus necesidades.
- **Rendimiento:** La transcripción y la traducción se realizan en CPU de forma predeterminada. Si dispones de GPU, podrías modificar el script para aprovecharla y acelerar el proceso.
- **FFmpeg:** Asegúrate de que `ffmpeg` está instalado y accesible desde la línea de comandos.
- **Personalización:** Puedes ampliar el script para incluir manejo de errores, logs o incluso una interfaz gráfica.

## Licencia

Este proyecto se distribuye bajo la [Licencia MIT](LICENSE).

---

¡Disfruta del uso del generador de subtítulos y traducciones!

