import os, time, uuid, base64, requests, json
from typing import List, Dict, Any

AUTH_URL = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
API_BASE = os.getenv("GIGACHAT_API_URL", "https://gigachat.devices.sberbank.ru/api/v1")
SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")  # GIGACHAT_API_PERS | GIGACHAT_API_B2B | GIGACHAT_API_CORP

# You can specify either GIGACHAT_AUTH (base64(client_id:client_secret)) or pair GIGACHAT_CLIENT_ID/GIGACHAT_CLIENT_SECRET
AUTH_B64 = os.getenv("GIGACHAT_AUTH")
CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")

VERIFY_SSL = os.getenv("GIGACHAT_VERIFY", "true").lower() not in {"0","false","no"}

class _TokenCache:
    access_token: str | None = None
    expires_at: float = 0.0

def _auth_header_value() -> str:
    if AUTH_B64:
        return f"Basic {AUTH_B64.strip()}"
    if CLIENT_ID and CLIENT_SECRET:
        raw = f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")
        return f"Basic {base64.b64encode(raw).decode()}"
    raise AssertionError("Provide GIGACHAT_AUTH or GIGACHAT_CLIENT_ID/GIGACHAT_CLIENT_SECRET in env/secrets")


def _get_token() -> str:
    now = time.time()
    if _TokenCache.access_token and _TokenCache.expires_at - now > 60:  # 60s safety
        return _TokenCache.access_token

    headers = {
        "Authorization": _auth_header_value(),
        "Content-Type": "application/x-www-form-urlencoded",
        "RqUID": str(uuid.uuid4()),
    }
    data = {"scope": SCOPE}
    # OAuth: some installations also require "grant_type=client_credentials"; add if env toggled
    if os.getenv("GIGACHAT_GRANT_TYPE", "").strip():
        data["grant_type"] = os.getenv("GIGACHAT_GRANT_TYPE")

    resp = requests.post(AUTH_URL, headers=headers, data=data, timeout=30, verify=VERIFY_SSL)
    if resp.status_code != 200:
        raise RuntimeError(f"GigaChat OAuth error {resp.status_code}: {resp.text}")
    payload = resp.json()
    token = payload.get("access_token") or payload.get("accessToken")
    exp = payload.get("expires_at") or (now + 25*60)  # default 25min TTL
    if not token:
        raise RuntimeError(f"GigaChat OAuth: token not found in response: {payload}")
    _TokenCache.access_token = token
    _TokenCache.expires_at = float(exp) if isinstance(exp, (int, float)) else now + 25*60
    return token


class GigaChat:
    def __init__(self):
        # model name may vary, check your account (examples: "GigaChat", "GigaChat:latest", "GigaChat-Pro")
        self.model = os.getenv("GIGACHAT_MODEL", "GigaChat")

    def chat(self, messages: List[Dict[str, Any]], temperature: float = 0.2, max_tokens: int = 800) -> str:
        token = _get_token()
        url = f"{API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        r = requests.post(url, headers=headers, json=body, timeout=60, verify=VERIFY_SSL)
        if r.status_code != 200:
            raise RuntimeError(f"GigaChat error {r.status_code}: {r.text}")
        data = r.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
