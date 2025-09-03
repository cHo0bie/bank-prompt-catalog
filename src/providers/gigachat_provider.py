import os, time, uuid, base64, requests
from typing import List, Dict, Any

AUTH_URL = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
API_BASE = os.getenv("GIGACHAT_API_URL", "https://gigachat.devices.sberbank.ru/api/v1")
SCOPE    = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")  # PERS | B2B | CORP

AUTH_B64 = os.getenv("GIGACHAT_AUTH")  # base64(client_id:client_secret)
CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")

# SSL handling:
# 1) If GIGACHAT_CA_BUNDLE points to a file, use it.
# 2) Else, read GIGACHAT_VERIFY=true/false (string). Default: true.
CA_BUNDLE = os.getenv("GIGACHAT_CA_BUNDLE")
if CA_BUNDLE and os.path.exists(CA_BUNDLE):
    VERIFY = CA_BUNDLE
else:
    VERIFY = os.getenv("GIGACHAT_VERIFY", "true").lower() not in {"0","false","no"}

class _TokenCache:
    token: str | None = None
    exp: float = 0.0

def _auth_header() -> str:
    if AUTH_B64:
        return f"Basic {AUTH_B64.strip()}"
    if CLIENT_ID and CLIENT_SECRET:
        import base64 as b64
        raw = f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")
        return "Basic " + b64.b64encode(raw).decode("utf-8")
    raise AssertionError("Provide GIGACHAT_AUTH or GIGACHAT_CLIENT_ID/GIGACHAT_CLIENT_SECRET")

def _get_token() -> str:
    now = time.time()
    if _TokenCache.token and (_TokenCache.exp - now) > 60:
        return _TokenCache.token

    headers = {
        "Authorization": _auth_header(),
        "Content-Type": "application/x-www-form-urlencoded",
        "RqUID": str(uuid.uuid4()),
    }
    data = {"scope": SCOPE}
    gt = os.getenv("GIGACHAT_GRANT_TYPE", "").strip()
    if gt:
        data["grant_type"] = gt

    resp = requests.post(AUTH_URL, headers=headers, data=data, timeout=40, verify=VERIFY)
    if resp.status_code != 200:
        raise RuntimeError(f"GigaChat OAuth error {resp.status_code}: {resp.text}")
    payload = resp.json()
    token = payload.get("access_token") or payload.get("accessToken")
    if not token:
        raise RuntimeError(f"GigaChat OAuth: token not found in response: {payload}")
    _TokenCache.token = token
    # ttl: 25 min by default if not provided
    exp = payload.get("expires_at")
    _TokenCache.exp = float(exp) if isinstance(exp, (int, float)) else (now + 25*60)
    return token

class GigaChat:
    def __init__(self):
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
        r = requests.post(url, headers=headers, json=body, timeout=60, verify=VERIFY)
        if r.status_code != 200:
            raise RuntimeError(f"GigaChat error {r.status_code}: {r.text}")
        data = r.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
