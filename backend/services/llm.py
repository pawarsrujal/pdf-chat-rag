"""
LLM service using Groq (LLaMA 3.x).
"""

import os
from groq import Groq


class LLMService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")

        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"

    def generate(self, prompt: str) -> str:
        """
        Generate a full response from the LLM (non-streaming).
        """

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI research assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=768,   # safe for Windows / low RAM
            stream=False      # 🔒 FORCE full response
        )

        return completion.choices[0].message.content.strip()
