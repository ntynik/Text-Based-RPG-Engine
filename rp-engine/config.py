import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if API_KEY is None:
    raise RuntimeError("OPENROUTER_API_KEY was not found.")

MODEL_ID = "deepseek/deepseek-v4-flash-0731"
TEMPERATURE = 0.7
SYSTEM_PROMPT = "You are a concise assistant. Never use more than 3 sentences in your answers."
VERSION = 0.1