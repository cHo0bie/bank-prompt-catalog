import json, os
from dotenv import load_dotenv
from .providers.openai_provider import OpenAIChat
from .providers.gigachat_provider import GigaChat

def get_provider():
    load_dotenv()
    prov = os.getenv('PROVIDER', 'openai').lower()
    if prov == 'gigachat':
        return GigaChat()
    return OpenAIChat()

def pretty(obj): 
    return json.dumps(obj, ensure_ascii=False, indent=2)
