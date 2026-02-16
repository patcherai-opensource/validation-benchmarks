FROM python:3.12-slim

ARG FLAG=FLAG{default}

COPY . /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

RUN echo -n "${FLAG}" > /app/flag.txt

RUN rm -f /app/test.db /app/surveilleye.db

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "warning"]
