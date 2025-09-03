
import os
try:
    from .providers.openai_provider import OpenAIChat
except Exception:
    OpenAIChat = None

try:
    from .providers.gigachat_provider import GigaChatChat
except Exception:
    GigaChatChat = None

def get_provider():
    """
    If GigaChat secrets/env present -> use GigaChatChat.
    Else fall back to OpenAIChat (requires OPENAI_API_KEY).
    """
    use_giga = bool(os.environ.get("GIGACHAT_AUTH_KEY") or os.environ.get("GIGACHAT_AUTH")
                    or os.environ.get("GIGACHAT_CLIENT_ID"))
    if use_giga and GigaChatChat:
        return GigaChatChat()
    if OpenAIChat:
        return OpenAIChat()
    raise RuntimeError("No provider available: set GIGACHAT_* or OPENAI_* secrets.")
