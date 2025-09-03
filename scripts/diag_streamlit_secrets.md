Вставьте в начало `demo_streamlit.py` рядом с импортами для быстрой проверки окружения:

```python
import os, streamlit as st
with st.sidebar.expander("Диагностика окружения"):
    st.write("PROVIDER:", os.getenv("PROVIDER"))
    st.write("GIGACHAT_MODEL:", os.getenv("GIGACHAT_MODEL"))
    st.write("AUTH header present:", bool(os.getenv("GIGACHAT_AUTH") or (os.getenv("GIGACHAT_CLIENT_ID") and os.getenv("GIGACHAT_CLIENT_SECRET"))))
    st.write("SCOPE:", os.getenv("GIGACHAT_SCOPE"))
    st.write("AUTH_URL:", os.getenv("GIGACHAT_AUTH_URL"))
    st.write("API_URL:", os.getenv("GIGACHAT_API_URL"))
```
