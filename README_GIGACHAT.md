
# GigaChat enablement patch

Этот патч добавляет поддержку провайдера **GigaChat** и авто‑выбор:
- если заданы переменные/секреты `GIGACHAT_*` → используется GigaChat;
- иначе остаётся OpenAI (как в оригинале).

## Файлы
- `src/providers/gigachat_provider.py` — адаптер GigaChat.
- `src/utils.py` — авто‑выбор провайдера.

## Streamlit Secrets (пример)

```toml
GIGACHAT_AUTH_KEY = "base64(client_id:client_secret)"
GIGACHAT_SCOPE    = "GIGACHAT_API_PERS"
GIGACHAT_MODEL    = "GigaChat-Pro"
GIGACHAT_VERIFY   = "false"    # если видите CERTIFICATE_VERIFY_FAILED

# если хотите оставить OpenAI — просто не задавайте GIGACHAT_* и укажите:
# OPENAI_API_KEY = "sk-..."
# OPENAI_API_BASE = "https://api.openai.com/v1"
```
