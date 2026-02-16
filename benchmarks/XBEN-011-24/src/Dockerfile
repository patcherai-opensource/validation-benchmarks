FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Plant flag at build time
ARG FLAG="flag{default-flag-placeholder}"
RUN echo "${FLAG}" > secret.txt

# Create static directory for temp files
RUN mkdir -p static

EXPOSE 5000

ENV FLASK_APP=app.py

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
