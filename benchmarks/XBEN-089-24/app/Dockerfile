FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Accept flag as build argument and set as environment variable
# (keeping existing pattern from base environment)
ARG FLAG
ENV FLAG=${FLAG}

EXPOSE 5003

CMD ["python", "app.py"]
