FROM python:3.9-slim

RUN pip3 install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0 python-multipart==0.0.6 jinja2==3.1.2 aiofiles==23.2.1

WORKDIR /app

COPY main.py /app/main.py
COPY templates/ /app/templates/

RUN mkdir -p /app/storage/assets /app/storage/entries/articles /app/storage/entries/feedback

ARG FLAG
RUN printf '%s' "${FLAG}" > /app/flag.txt && chmod 400 /app/flag.txt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
