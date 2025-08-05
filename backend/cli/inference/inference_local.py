from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
from pathlib import Path

class LocalLLM:
    _model = None
    _tokenizer = None
    _model_name = "google/gemma-3n-E4B"  # Default fallback
    _model_path = None

    @classmethod
    def _get_model_path(cls):
        """Get the path to downloaded models"""
        if cls._model_path:
            return cls._model_path
            
        # Check for downloaded models in user directory
        models_dir = Path.home() / ".overseer" / "models"
        config_file = Path.home() / ".overseer" / "model_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                models = config.get("models", {})
                
                # Find the first available downloaded model
                for model_id, model_info in models.items():
                    if model_info.get("status") == "downloaded":
                        model_path = Path(model_info["path"])
                        if model_path.exists():
                            cls._model_path = str(model_path)
                            cls._model_name = model_id
                            return cls._model_path
                            
            except Exception as e:
                print(f"Error reading model config: {e}")
        
        # Fallback to downloading from HuggingFace
        return cls._model_name

    def __init__(self):
        if LocalLLM._model is None or LocalLLM._tokenizer is None:
            model_path = self._get_model_path()
            
            try:
                LocalLLM._tokenizer = AutoTokenizer.from_pretrained(model_path)
                LocalLLM._model = AutoModelForCausalLM.from_pretrained(
                    model_path, 
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32, 
                    device_map="auto"
                )
                print(f"✅ Loaded local model from: {model_path}")
            except Exception as e:
                print(f"❌ Error loading model from {model_path}: {e}")
                print("📝 Run 'python -m backend.cli.model_manager' to download models")
                raise

    def run(self, prompt: str) -> str:
        try:
            inputs = LocalLLM._tokenizer(prompt, return_tensors="pt").to(LocalLLM._model.device)
            with torch.no_grad():
                outputs = LocalLLM._model.generate(
                    **inputs, 
                    max_new_tokens=256, 
                    do_sample=True, 
                    temperature=0.7,
                    pad_token_id=LocalLLM._tokenizer.eos_token_id
                )
            response = LocalLLM._tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from the response if present
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response if response else "[Local LLM] No response generated."
            
        except Exception as e:
            return f"[Local LLM Error] {e}" 