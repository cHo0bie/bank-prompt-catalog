from __future__ import annotations
import json, re
from jsonschema import validate as js_validate, Draft202012Validator
from jsonschema.exceptions import ValidationError

def extract_json(text: str) -> str | None:
    # Try to find the first JSON object in text
    m = re.search(r'\{[\s\S]*\}', text)
    if not m:
        return None
    snippet = m.group(0)
    return snippet

def try_repair(text: str) -> str | None:
    # naive repairs: fix trailing commas and quotes
    snippet = extract_json(text)
    if not snippet:
        return None
    # remove trailing commas before } or ]
    snippet = re.sub(r',\s*([}\]])', r'\1', snippet)
    return snippet

def validate_against_schema(obj: dict, schema: dict) -> tuple[bool, str | None]:
    try:
        Draft202012Validator(schema).validate(obj)
        return True, None
    except ValidationError as e:
        return False, str(e)

def ensure_valid(text: str, schema: dict) -> tuple[dict | None, str | None]:
    # Try direct parse
    try:
        data = json.loads(text)
        ok, err = validate_against_schema(data, schema)
        if ok:
            return data, None
    except Exception:
        pass

    # Try repair
    snippet = try_repair(text)
    if not snippet:
        return None, "JSON not found"
    try:
        data = json.loads(snippet)
        ok, err = validate_against_schema(data, schema)
        if ok:
            return data, None
        return None, err
    except Exception as e:
        return None, f"JSON parse error: {e}"
