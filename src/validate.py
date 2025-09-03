from __future__ import annotations
import json, re

def _strip_bom(text: str) -> str:
    return text.lstrip('\ufeff')

def _strip_code_fences(text: str) -> str:
    # ```json ... ``` or ``` ... ```
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    return m.group(1) if m else text

def _normalize_quotes(text: str) -> str:
    # replace smart quotes with straight quotes
    table = str.maketrans({
        '“': '"', '”': '"', '„': '"', '«': '"', '»': '"',
        '’': "'", '‘': "'"
    })
    return text.translate(table)

def _quote_unquoted_keys(text: str) -> str:
    # add quotes around unquoted keys at start-of-line or after { or , (not inside strings)
    # naive but effective for small objects
    def repl(m):
        return f'{m.group(1)}"{m.group(2)}"{m.group(3)}'
    pattern = r'([\{,]\s*)([A-Za-z_][A-Za-z0-9_\-]*)(\s*:)'
    return re.sub(pattern, repl, text)

def _single_to_double_quotes(text: str) -> str:
    # convert single-quoted JSON-like to double-quoted (outside of already-double quoted segments)
    # careful: do not touch numbers/null/true/false
    # First, ensure keys are quoted (with either ' or ")
    text = re.sub(r"'([A-Za-z_][A-Za-z0-9_\-]*)'\s*:", r'"\1":', text)
    # Then, values that are single-quoted strings
    text = re.sub(r":\s*'([^']*)'", r': "\1"', text)
    return text

def extract_json(text: str) -> str | None:
    text = _strip_bom(text)
    text = _strip_code_fences(text)
    text = _normalize_quotes(text).strip()
    # If there is extra commentary around JSON — take the first {...}
    m = re.search(r'\{[\s\S]*\}', text)
    if not m:
        return None
    snippet = m.group(0)
    snippet = _quote_unquoted_keys(snippet)
    snippet = _single_to_double_quotes(snippet)
    # remove trailing commas before } or ]
    snippet = re.sub(r',\s*([}\]])', r'\1', snippet)
    return snippet

def ensure_valid(text: str, schema: dict) -> tuple[dict | None, str | None]:
    # 1) Try strict JSON directly
    try:
        data = json.loads(text)
        from jsonschema import Draft202012Validator
        Draft202012Validator(schema).validate(data)
        return data, None
    except Exception:
        pass

    # 2) Try to extract/repair
    snippet = extract_json(text)
    if not snippet:
        return None, "JSON not found"
    try:
        data = json.loads(snippet)
        from jsonschema import Draft202012Validator
        Draft202012Validator(schema).validate(data)
        return data, None
    except Exception as e:
        return None, f"JSON parse error: {e}"
