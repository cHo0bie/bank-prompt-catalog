from __future__ import annotations
import json, re
from typing import Any, Dict

def _strip_bom(text: str) -> str:
    return text.lstrip('\ufeff')

def _strip_code_fences(text: str) -> str:
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    return m.group(1) if m else text

def _normalize_quotes(text: str) -> str:
    table = str.maketrans({
        '“': '"', '”': '"', '„': '"', '«': '"', '»': '"',
        '’': "'", '‘': "'"
    })
    return text.translate(table)

def _quote_unquoted_keys(text: str) -> str:
    def repl(m):
        return f'{m.group(1)}"{m.group(2)}"{m.group(3)}'
    pattern = r'([\{,]\s*)([A-Za-z_][A-Za-z0-9_\-]*)(\s*:)'
    return re.sub(pattern, repl, text)

def _single_to_double_quotes(text: str) -> str:
    text = re.sub(r"'([A-Za-z_][A-Za-z0-9_\-]*)'\s*:", r'"\1":', text)   # keys
    text = re.sub(r':\s*\'([^\']*)\'', r': "\1"', text)                   # values
    return text

def extract_json(text: str) -> str | None:
    text = _strip_bom(text)
    text = _strip_code_fences(text)
    text = _normalize_quotes(text).strip()
    m = re.search(r'\{[\s\S]*\}', text)
    if not m:
        return None
    snippet = m.group(0)
    snippet = _quote_unquoted_keys(snippet)
    snippet = _single_to_double_quotes(snippet)
    snippet = re.sub(r',\s*([}\]])', r'\1', snippet)  # trailing commas
    return snippet

def _coerce_enums(data: Any, schema: Dict[str, Any]) -> Any:
    """
    Best-effort: если в схеме есть enum и значение не попадает — пробуем привести:
    - строка 'fraud|card' -> 'fraud'
    - массив ['card','fraud'] -> 'card'
    - нормализуем регистр/пробелы
    Рекурсивно обходим вложенные объекты.
    """
    if isinstance(data, dict) and isinstance(schema, dict):
        props = schema.get("properties", {})
        for k, v in list(data.items()):
            subschema = props.get(k)
            if subschema:
                enum = subschema.get("enum")
                if enum and isinstance(v, str):
                    vv = v.strip()
                    if '|' in vv:
                        vv = vv.split('|', 1)[0].strip()
                    vv_low = vv.lower()
                    if vv in enum or vv_low in enum:
                        data[k] = vv_low if vv_low in enum else vv
                    else:
                        for token in re.split(r'[,/;| ]+', vv_low):
                            if token in enum:
                                data[k] = token
                                break
                elif enum and isinstance(v, list) and v:
                    first = None
                    for item in v:
                        if isinstance(item, str):
                            token = item.strip().lower()
                            if token in enum:
                                first = token
                                break
                            if '|' in token:
                                t0 = token.split('|', 1)[0].strip()
                                if t0 in enum:
                                    first = t0
                                    break
                    if first:
                        data[k] = first
                else:
                    data[k] = _coerce_enums(v, subschema)
            else:
                data[k] = _coerce_enums(v, {})
        return data
    elif isinstance(data, list):
        return [_coerce_enums(x, schema.get("items", {})) for x in data]
    else:
        return data

def ensure_valid(text: str, schema: dict) -> tuple[dict | None, str | None]:
    # 1) Try strict JSON directly
    try:
        data = json.loads(text)
        from jsonschema import Draft202012Validator
        Draft202012Validator(schema).validate(data)
        return data, None
    except Exception:
        pass

    # 2) Extract & repair
    snippet = extract_json(text)
    if not snippet:
        return None, "JSON not found"
    try:
        data = json.loads(snippet)
        # enum coercion before final validation
        data = _coerce_enums(data, schema)
        from jsonschema import Draft202012Validator
        Draft202012Validator(schema).validate(data)
        return data, None
    except Exception as e:
        return None, f"JSON parse error: {e}"
