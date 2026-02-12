FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP app.py

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY website /app/

# Startup script writes flag to a file at runtime and then starts the app
RUN echo '#!/bin/bash\necho -n "${FLAG:-PLACEHOLDER_FLAG}" > /opt/flag.txt\nchmod 644 /opt/flag.txt\nunset FLAG\nexec flask run --host=0.0.0.0 -p 80' > /start.sh && chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
