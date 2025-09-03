
import os, requests

class GigaChatChat:
    """
    Minimal adapter for Sber GigaChat API to match OpenAIChat(chat) interface.
    Secrets/env:
      GIGACHAT_AUTH_KEY  - base64(client_id:client_secret) from portal
      GIGACHAT_SCOPE      - e.g. GIGACHAT_API_PERS
      GIGACHAT_MODEL      - e.g. GigaChat-Pro
      GIGACHAT_VERIFY     - "true"/"false" (TLS verify)
    """
    def __init__(self, model=None):
        self.model = model or os.environ.get("GIGACHAT_MODEL") or "GigaChat-Pro"
        self.scope = os.environ.get("GIGACHAT_SCOPE") or "GIGACHAT_API_PERS"
        self.auth_key = (os.environ.get("GIGACHAT_AUTH_KEY")
                         or os.environ.get("GIGACHAT_AUTH"))
        vr = (os.environ.get("GIGACHAT_VERIFY","true").strip().lower())
        self.verify = False if vr in ("0","false","no","off") else True
        self._token = None

    def _get_token(self):
        import uuid
        if self._token: return self._token
        headers = {
            "Authorization": f"Basic {self.auth_key}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4())
        }
        data = {"scope": self.scope}
        import requests as _rq
        r = _rq.post("https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                          headers=headers, data=data, timeout=60, verify=self.verify)
        r.raise_for_status()
        self._token = r.json()["access_token"]
        return self._token

    def chat(self, prompt: str, temperature: float=0.0) -> str:
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type":"application/json"}
        payload = {"model": self.model, "messages":[{"role":"user","content":prompt}], "temperature": temperature}
        import requests as _rq
        r = _rq.post("https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                          headers=headers, json=payload, timeout=120, verify=self.verify)
        if r.status_code == 401:
            self._token = None
            return self.chat(prompt, temperature=temperature)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
