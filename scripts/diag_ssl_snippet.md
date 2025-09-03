Добавьте в начало `demo_streamlit.py`:

```python
import os, streamlit as st
with st.sidebar.expander("TLS/Secrets"):
    st.write("PROVIDER:", os.getenv("PROVIDER"))
    st.write("GIGACHAT_MODEL:", os.getenv("GIGACHAT_MODEL"))
    st.write("CA_BUNDLE path:", os.getenv("GIGACHAT_CA_BUNDLE") or "—")
    st.write("VERIFY flag:", os.getenv("GIGACHAT_VERIFY","true"))
    st.write("AUTH set:", bool(os.getenv("GIGACHAT_AUTH") or (os.getenv("GIGACHAT_CLIENT_ID") and os.getenv("GIGACHAT_CLIENT_SECRET"))))
```
