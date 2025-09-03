from pathlib import Path
from jinja2 import Template

ROOT = Path(__file__).resolve().parents[1]

def load(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')

def render_template(template_path: str, **kwargs) -> str:
    tpl = Template(load(template_path))
    return tpl.render(**kwargs)
