FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install flask

COPY app.py .

ARG FLAG
ENV FLAG=${FLAG:-@FLAG@}

EXPOSE 80

CMD ["python", "app.py"]
