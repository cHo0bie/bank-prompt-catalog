# Каталог промптов (банковские сценарии)

Готовый набор системных подсказок, шаблонов и **контрактов на строгий JSON** для типовых задач банковского ассистента: FAQ, извлечение реквизитов, обработка жалоб, статус платежа. 
В комплекте есть **валидация pydantic**, тестовые кейсы и **демо на Streamlit**.

> Сделано в стиле: *system/role/context → few‑shot → строгий JSON + repair → оценка валидности*.

## Быстрый старт

```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config_example.env .env  # и заполните ключи / провайдера
# Локальный прогон примера (FAQ)
python src/runner.py --task faq --question "Как перевести деньги на карту другого банка?"
# Веб-демо
streamlit run demo_streamlit.py
```

Провайдеры: **OpenAI** (совместимый API) и **GigaChat**. Выбирается переменной `PROVIDER` в `.env`. 
В репозитории есть тонкие адаптеры для обоих. Ключи храните только в `.env`/секретах деплоя.

## Структура

```
bank-prompt-catalog/
├── README.md
├── LICENSE
├── requirements.txt
├── config_example.env
├── prompts/
│   ├── system_ru.md
│   ├── style_ru.md
│   ├── policies_ru.md
│   ├── templates/
│   │   ├── faq_ru.prompt
│   │   ├── extract_requisites_ru.prompt
│   │   ├── complaint_response_ru.prompt
│   │   └── payment_status_ru.prompt
│   ├── schemas/
│   │   ├── faq.schema.json
│   │   ├── extract_requisites.schema.json
│   │   ├── complaint.schema.json
│   │   └── payment_status.schema.json
│   └── tests/
│       ├── faq.jsonl
│       ├── extract_requisites.jsonl
│       ├── complaint.jsonl
│       └── payment_status.jsonl
├── src/
│   ├── runner.py
│   ├── validate.py
│   ├── models.py
│   ├── prompt_loader.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── openai_provider.py
│   │   └── gigachat_provider.py
│   └── utils.py
├── demo_streamlit.py
└── examples/
    ├── faq_example_request.json
    └── faq_example_response.json
```

## Репейр (починка) JSON
Если модель вернула невалидный JSON, `validate.py` делает мягкий **repair**: пытается извлечь JSON фрагмент, исправить запятые/кавычки и повторить валидацию. При неуспехе `runner.py` может сделать 1 ретрай с более строгим указанием формата.

## Тесты/оценка
В `prompts/tests/*.jsonl` лежат небольшие наборы входов для ручной/полуавтоматической оценки. 
Метрики: **валидность JSON** (цель ≥98%), длина ответа, заметки по faithfulness.

## Деплой демо
- **Streamlit Cloud**: залейте репо, в панели укажите команду запуска `streamlit run demo_streamlit.py`, добавьте переменные окружения (`.env` через Secrets).
- **Docker** (локально): соберите образ командой:
  ```bash
  docker build -t bank-prompt-demo .
  docker run -p 8501:8501 --env-file .env bank-prompt-demo
  ```

## Правила/PII
Перед отправкой юзерских данных включайте анонимизацию/маскирование (см. `policies_ru.md`). Не храните PII в логах.
