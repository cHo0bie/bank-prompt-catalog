import os, requests

class OpenAIChat:
    def __init__(self):
        self.base = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self.key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        assert self.key, 'OPENAI_API_KEY is required'
    def chat(self, messages, temperature=0.2, max_tokens=800):
        url = f"{self.base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
