import os
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env
load_dotenv()

# Asigna la API key a una variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
