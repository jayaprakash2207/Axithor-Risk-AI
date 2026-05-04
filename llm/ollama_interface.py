import json
from typing import Optional

import requests


class OllamaClient:
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, temperature: float = 0.2) -> Optional[str]:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False,
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("response")
        except Exception as exc:
            print(f"OllamaClient: request failed ({exc}); falling back to heuristic analysis")
            return None
