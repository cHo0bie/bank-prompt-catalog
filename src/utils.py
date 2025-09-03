
import os, json

# Optional Streamlit
try:
    import streamlit as st  # type: ignore
except Exception:
    st = None  # type: ignore

def _sec(*names, default=None):
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    if st is not None:
        try:
            for n in names:
                v = st.secrets.get(n)  # type: ignore[attr-defined]
                if v:
                    return str(v)
        except Exception:
            pass
    return default

# ---------------- Providers ----------------

class OpenAIChat:
    def __init__(self, model=None):
        self.key = _sec("OPENAI_API_KEY")
        self.base = _sec("OPENAI_API_BASE", default="https://api.openai.com/v1")
        self.model = model or _sec("OPENAI_MODEL", default="gpt-4o-mini")
        assert self.key, "OPENAI_API_KEY is required"

    def chat(self, messages_or_prompt, temperature: float = 0.0, max_tokens=None, **kwargs) -> str:
        import requests
        # Accept string or list of {role, content}
        if isinstance(messages_or_prompt, str):
            messages = [{"role": "user", "content": messages_or_prompt}]
        else:
            messages = messages_or_prompt
        payload = {"model": self.model, "messages": messages, "temperature": temperature}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        r = requests.post(f"{self.base}/chat/completions", headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

class GigaChatChat:
    def __init__(self, model=None):
        import base64
        self.model = model or _sec("GIGACHAT_MODEL", default="GigaChat-Pro")
        self.scope = _sec("GIGACHAT_SCOPE", default="GIGACHAT_API_PERS")
        self.auth_key = _sec("GIGACHAT_AUTH_KEY") or _sec("GIGACHAT_AUTH")
        if not self.auth_key:
            cid = _sec("GIGACHAT_CLIENT_ID")
            csec = _sec("GIGACHAT_CLIENT_SECRET")
            if cid and csec:
                self.auth_key = base64.b64encode(f"{cid}:{csec}".encode()).decode()
        vr = (_sec("GIGACHAT_VERIFY", default="true") or "true").strip().lower()
        self.verify = False if vr in ("0", "false", "no", "off") else True
        assert self.auth_key, "GIGACHAT_AUTH_KEY (или CLIENT_ID/CLIENT_SECRET) не задан"
        self._token = None

    def _get_token(self) -> str:
        import uuid, requests
        if self._token:
            return self._token
        headers = {
            "Authorization": f"Basic {self.auth_key}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
        }
        data = {"scope": self.scope}
        r = requests.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers=headers,
            data=data,
            timeout=60,
            verify=self.verify,
        )
        r.raise_for_status()
        self._token = r.json()["access_token"]
        return self._token

    def chat(self, messages_or_prompt, temperature: float = 0.0, max_tokens=None, **kwargs) -> str:
        import requests, uuid
        tok = self._get_token()
        if isinstance(messages_or_prompt, str):
            messages = [{"role": "user", "content": messages_or_prompt}]
        else:
            messages = messages_or_prompt
        payload = {"model": self.model, "messages": messages, "temperature": temperature}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        headers = {
            "Authorization": f"Bearer {tok}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
        }
        r = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
            verify=self.verify,
        )
        if r.status_code == 401:
            self._token = None
            return self.chat(messages_or_prompt, temperature=temperature, max_tokens=max_tokens, **kwargs)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

def get_provider():
    if _sec("GIGACHAT_AUTH_KEY") or _sec("GIGACHAT_AUTH") or _sec("GIGACHAT_CLIENT_ID"):
        return GigaChatChat()
    return OpenAIChat()

# --------------- Utils ----------------
def pretty(x) -> str:
    try:
        if isinstance(x, str):
            return json.dumps(json.loads(x), ensure_ascii=False, indent=2)
        return json.dumps(x, ensure_ascii=False, indent=2)
    except Exception:
        return str(x)
