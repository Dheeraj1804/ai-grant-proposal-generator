from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

print("Python is running from:", BASE_DIR)
print(".env file exists:", ENV_PATH.exists())

load_dotenv(dotenv_path=ENV_PATH, override=True)

api_key = os.getenv("OPENROUTER_API_KEY")

print("API key detected:", bool(api_key and api_key.strip()))

if api_key:
    print("API key length:", len(api_key.strip()))