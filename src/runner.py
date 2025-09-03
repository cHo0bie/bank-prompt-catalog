import argparse, json
from src.prompt_loader import render_template, load
from src.utils import get_provider, pretty
from src.validate import ensure_valid

TASKS = {
    "faq": {
        "template": "prompts/templates/faq_ru.prompt",
        "schema": "prompts/schemas/faq.schema.json",
        "inputs": ["question"]
    },
    "extract": {
        "template": "prompts/templates/extract_requisites_ru.prompt",
        "schema": "prompts/schemas/extract_requisites.schema.json",
        "inputs": ["text"]
    },
    "complaint": {
        "template": "prompts/templates/complaint_response_ru.prompt",
        "schema": "prompts/schemas/complaint.schema.json",
        "inputs": ["complaint"]
    },
    "payment": {
        "template": "prompts/templates/payment_status_ru.prompt",
        "schema": "prompts/schemas/payment_status.schema.json",
        "inputs": ["facts_json"]
    }
}

def main():
    ap = argparse.ArgumentParser(description="Run LLM with strict JSON contract")
    ap.add_argument("--task", choices=TASKS.keys(), required=True)
    ap.add_argument("--question")  # for faq
    ap.add_argument("--text")      # for extract
    ap.add_argument("--complaint") # for complaint
    ap.add_argument("--facts_json")# for payment
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max_tokens", type=int, default=800)
    args = ap.parse_args()

    conf = TASKS[args.task]
    # load fragments
    system = load("prompts/system_ru.md")
    style = load("prompts/style_ru.md")
    policies = load("prompts/policies_ru.md")
    prompt = render_template(conf["template"], system=system, style=style, policies=policies,
                             question=args.question, text=args.text, complaint=args.complaint, facts_json=args.facts_json)

    provider = get_provider()
    messages = [{"role":"system","content":system}, {"role":"user","content":prompt}]
    raw = provider.chat(messages, temperature=args.temperature, max_tokens=args.max_tokens)

    schema = json.loads(load(conf["schema"]))    
    data, err = ensure_valid(raw, schema)
    print("
=== RAW ===
", raw)
    if err:
        print("
✖ Валидация не прошла:", err)
    else:
        print("
✓ Валидация пройдена. JSON:
", pretty(data))

if __name__ == "__main__":
    main()
