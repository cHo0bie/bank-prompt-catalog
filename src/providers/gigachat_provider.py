import os, requests

class GigaChat:
    def __init__(self):
        self.base = os.getenv('GIGACHAT_API_URL', 'https://gigachat.devices.sberbank.ru/api/v1')
        self.key = os.getenv('GIGACHAT_API_KEY')
        self.model = os.getenv('GIGACHAT_MODEL', 'GigaChat-Pro')
        assert self.key, 'GIGACHAT_API_KEY is required'
    def chat(self, messages, temperature=0.2, max_tokens=800):
        # Проверьте актуальную спецификацию API GigaChat и при необходимости скорректируйте поля запроса
        url = f"{self.base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        # Предполагаем ответ в стиле OpenAI; при иных форматах см. документацию провайдера
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
