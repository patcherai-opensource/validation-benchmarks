FROM python:3.12

COPY . /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

# Accept FLAG as build argument and set as environment variable
ARG FLAG
ENV FLAG=${FLAG:-FLAG{default_flag}}

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
