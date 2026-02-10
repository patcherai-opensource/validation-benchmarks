FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py app.py
COPY templates/ templates/

# Build-time flag injection - write to file, NOT environment variable
ARG FLAG
RUN echo "${FLAG}" > /app/flag.txt && chmod 600 /app/flag.txt

CMD ["python3", "app.py"]
