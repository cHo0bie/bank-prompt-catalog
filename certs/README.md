# Кастомные сертификаты для GigaChat (опционально)

Если в облаке возникает `SSLCertVerificationError` при обращении к
`https://ngw.devices.sberbank.ru:9443/api/v2/oauth`, положите сюда
корневой/промежуточные сертификаты цепочки в файл, например:

```
certs/gigachat_ca.pem
```

И задайте переменную (в Secrets Streamlit Cloud):

```
GIGACHAT_CA_BUNDLE="/mount/src/bank-prompt-catalog/certs/gigachat_ca.pem"
```

Библиотека `requests` будет использовать этот путь для проверки TLS.
Для быстрых демо можно временно поставить `GIGACHAT_VERIFY="false"`,
но для продакшена используйте корректный CA bundle.
