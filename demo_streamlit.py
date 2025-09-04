import streamlit as st, json
from src.prompt_loader import load, render_template
from src.utils import get_provider, pretty
from src.validate import ensure_valid

st.set_page_config(page_title="Bank Prompt Catalog Demo", page_icon="🤖", layout="wide")

st.title("Каталог промптов — демо")

tab = st.sidebar.radio("Сценарий", ["FAQ", "Извлечение реквизитов", "Жалоба", "Статус платежа"])

system = load("prompts/system_ru.md")
style = load("prompts/style_ru.md")
policies = load("prompts/policies_ru.md")

provider = get_provider()

def run(prompt_path, schema_path, **kwargs):
    prompt = render_template(prompt_path, system=system, style=style, policies=policies, **kwargs)
    st.subheader("Сформированный prompt") 
    st.code(prompt, language="markdown")
    with st.spinner("Запрос к LLM..."):
        raw = provider.chat([{"role":"system","content":system},{"role":"user","content":prompt}], temperature=0.2, max_tokens=800)
    st.subheader("сырой ответ") 
    st.code(raw, language="json")
    schema = json.loads(load(schema_path))
    data, err = ensure_valid(raw, schema)
    if err:
        st.error(f"Валидация не прошла: {err}")
    else:
        st.success("Валидация пройдена") 
        st.code(pretty(data), language="json")

if tab == "FAQ":
    q = st.text_area("Вопрос клиента", "Как перевести деньги на карту другого банка?")
    if st.button("Запустить", key="faq"):
        run("prompts/templates/faq_ru.prompt", "prompts/schemas/faq.schema.json", question=q)

elif tab == "Извлечение реквизитов":
    t = st.text_area("Текст с реквизитами", "ООО Ромашка, ИНН 7701234567, КПП 770101001, р/с 40702810900000012345 в ПАО СуперБанк, БИК 044525225, к/с 30101810400000000225")    
    if st.button("Запустить", key="extract"):
        run("prompts/templates/extract_requisites_ru.prompt", "prompts/schemas/extract_requisites.schema.json", text=t)

elif tab == "Жалоба":
    c = st.text_area("Текст жалобы", "С моей карты списали деньги без согласия. Поддержка не отвечает уже 2 часа.")
    if st.button("Запустить", key="complaint"):
        run("prompts/templates/complaint_response_ru.prompt", "prompts/schemas/complaint.schema.json", complaint=c)

else:
    f = st.text_area("Факты о платеже (JSON)", '{"payment_id":"abc123","status":"pending","amount":1500,"currency":"RUB","timestamp":"2025-09-02T10:05:00+03:00"}')
    if st.button("Запустить", key="payment"):
        run("prompts/templates/payment_status_ru.prompt", "prompts/schemas/payment_status.schema.json", facts_json=f)
