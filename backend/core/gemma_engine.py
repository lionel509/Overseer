import os
from typing import Optional

# HuggingFace Transformers
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

# Google API imports (placeholder, only import if needed)
try:
    from google.cloud import aiplatform
    from google.oauth2 import service_account
except ImportError:
    aiplatform = None
    service_account = None

# ENV CONFIG
GEMMA_MODEL_PATH = os.environ.get("GEMMA_MODEL_PATH", "./models/overseer-gemma-3n")
GEMMA_USE_GOOGLE_API = os.environ.get("GEMMA_USE_GOOGLE_API", "false").lower() == "true"
GEMMA_GOOGLE_PROJECT = os.environ.get("GEMMA_GOOGLE_PROJECT")
GEMMA_GOOGLE_LOCATION = os.environ.get("GEMMA_GOOGLE_LOCATION", "us-central1")
GEMMA_GOOGLE_API_KEY = os.environ.get("GEMMA_GOOGLE_API_KEY")
GEMMA_GOOGLE_SA_JSON = os.environ.get("GEMMA_GOOGLE_SA_JSON")  # path to service account json

# Local model cache
_tokenizer = None
_model = None
_pipe = None

def _load_local_model():
    global _tokenizer, _model, _pipe
    if _tokenizer is None or _model is None or _pipe is None:
        _tokenizer = AutoTokenizer.from_pretrained(GEMMA_MODEL_PATH)
        _model = AutoModelForCausalLM.from_pretrained(GEMMA_MODEL_PATH, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
        _pipe = pipeline("text-generation", model=_model, tokenizer=_tokenizer, device=0 if torch.cuda.is_available() else -1)
    return _pipe

# Google API inference (placeholder)
def _google_api_generate(prompt: str) -> str:
    if not (aiplatform and service_account):
        raise ImportError("google-cloud-aiplatform is not installed.")
    if not (GEMMA_GOOGLE_PROJECT and GEMMA_GOOGLE_SA_JSON):
        raise ValueError("Google API project and service account JSON must be set in env.")
    creds = service_account.Credentials.from_service_account_file(GEMMA_GOOGLE_SA_JSON)
    aiplatform.init(project=GEMMA_GOOGLE_PROJECT, location=GEMMA_GOOGLE_LOCATION, credentials=creds)
    # This is a placeholder. Actual API call depends on Google Vertex AI API for Gemma 3n.
    # Replace with real code as needed.
    raise NotImplementedError("Google API inference not implemented. Use local model for now.")


def generate_response(query: str, context: Optional[str] = None) -> str:
    """
    Generate a response from Gemma 3n (local or Google API).
    """
    prompt = query if not context else f"Context: {context}\nUser: {query}"
    if GEMMA_USE_GOOGLE_API:
        return _google_api_generate(prompt)
    # Local inference
    pipe = _load_local_model()
    result = pipe(prompt, max_length=256, do_sample=True, temperature=0.7)
    return result[0]["generated_text"].strip() 