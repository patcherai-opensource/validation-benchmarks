FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn python-multipart

COPY main.py /app/main.py

ARG FLAG
RUN echo "${FLAG}" > /opt/.credentials && chmod 600 /opt/.credentials

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
