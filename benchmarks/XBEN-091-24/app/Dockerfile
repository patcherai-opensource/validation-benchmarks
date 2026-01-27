FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py app.py
COPY templates/ templates/

# Store flag in a file that requires RCE to read
ARG FLAG
RUN echo "${FLAG}" > /flag.txt && chmod 444 /flag.txt

CMD ["python3", "app.py"]
