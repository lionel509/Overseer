from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class LocalLLM:
    _model = None
    _tokenizer = None
    _model_name = "google/gemma-3n-E4B"  # Switched to Gemma 3B Instruct

    def __init__(self):
        if LocalLLM._model is None or LocalLLM._tokenizer is None:
            LocalLLM._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            LocalLLM._model = AutoModelForCausalLM.from_pretrained(self._model_name, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32, device_map="auto")

    def run(self, prompt: str) -> str:
        inputs = LocalLLM._tokenizer(prompt, return_tensors="pt").to(LocalLLM._model.device)
        with torch.no_grad():
            outputs = LocalLLM._model.generate(**inputs, max_new_tokens=256, do_sample=True, temperature=0.7)
        response = LocalLLM._tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from the response if present
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
        return response if response else "[Local LLM] No response generated." 