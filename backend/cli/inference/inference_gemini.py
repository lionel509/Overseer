import os
import google.generativeai as genai
import re

class GeminiAPI:
    # Maximum prompt length to prevent abuse
    MAX_PROMPT_LENGTH = 4000
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment variables")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt to prevent injection attacks"""
        # Remove null bytes
        prompt = prompt.replace('\x00', '')
        
        # Limit prompt length
        if len(prompt) > self.MAX_PROMPT_LENGTH:
            prompt = prompt[:self.MAX_PROMPT_LENGTH]
        
        return prompt

    def run(self, prompt: str) -> str:
        try:
            # Sanitize input
            sanitized_prompt = self._sanitize_prompt(prompt)
            
            # Generate response with safety settings
            response = self.model.generate_content(
                sanitized_prompt,
                safety_settings={
                    'HARASSMENT': 'BLOCK_MEDIUM_AND_ABOVE',
                    'HATE_SPEECH': 'BLOCK_MEDIUM_AND_ABOVE',
                    'SEXUALLY_EXPLICIT': 'BLOCK_MEDIUM_AND_ABOVE',
                    'DANGEROUS_CONTENT': 'BLOCK_MEDIUM_AND_ABOVE',
                }
            )
            return response.text
        except Exception as e:
            return f"[Gemini API Error] {e}" 