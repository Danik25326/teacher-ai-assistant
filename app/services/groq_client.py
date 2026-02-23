import json
import logging
from groq import Groq
from app.config import Config

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.model = Config.GROQ_MODEL
        if not self.api_key:
            logger.error("GROQ_API_KEY не задано")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)

    async def generate_content(self, prompt: str, system_prompt: str = "",
                               temperature=0.4, max_tokens=2000) -> dict:
        if not self.client:
            return {}
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            response_text = completion.choices[0].message.content
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Помилка Groq API: {e}")
            return {}
