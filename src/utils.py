import os, json
from dotenv import load_dotenv
# провайдеры
from .providers.openai_provider import OpenAIChat
from .providers.gigachat_provider import GigaChat

def _hydrate_env_from_streamlit_secrets():
    """
    На Streamlit Cloud значения хранятся в st.secrets.
    Прокинем их в os.environ, чтобы существующий код провайдеров ничего не менять.
    """
    try:
        import streamlit as st  # доступно только в рантайме Streamlit
        for k, v in st.secrets.items():
            # Секрет может быть строкой или вложенной секцией (dict). Нас интересуют простые пары.
            if isinstance(v, str) and k not in os.environ:
                os.environ[k] = v
    except Exception:
        # Локальный запуск без streamlit — просто пропускаем
        pass

def get_provider():
    # 1) .env локально
    load_dotenv()
    # 2) secrets на Streamlit
    _hydrate_env_from_streamlit_secrets()

    prov = os.getenv('PROVIDER', 'openai').lower()
    if prov == 'gigachat':
        return GigaChat()
    return OpenAIChat()

def pretty(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)
