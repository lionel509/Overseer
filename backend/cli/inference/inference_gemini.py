import os
import google.generativeai as genai

class GeminiAPI:
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def run(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"[Gemini API Error] {e}" 