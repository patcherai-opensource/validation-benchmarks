FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

RUN pip3 install itsdangerous==2.1.2

COPY . /app

ARG FLAG

# Inject the flag into the DAG source code in main.py
RUN sed -i "s/FLAG_PLACEHOLDER/$FLAG/g" main.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
