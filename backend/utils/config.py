import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama3-70b-instruct")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

# Warn if API key is not set, but don't crash
if not NVIDIA_API_KEY:
    import warnings
    warnings.warn("NVIDIA_API_KEY not set. LLM features will fail. Set it in .env file.")
