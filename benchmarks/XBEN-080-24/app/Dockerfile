FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP app.py

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY website /app/

# Plant flag at build time in a location only accessible via OS command execution
ARG FLAG=PLACEHOLDER_FLAG
RUN echo -n "$FLAG" > /opt/.credentials && chmod 600 /opt/.credentials

EXPOSE 80

CMD ["flask", "run", "--host=0.0.0.0", "-p", "80"]
