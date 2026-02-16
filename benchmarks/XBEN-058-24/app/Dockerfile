FROM python:3.12-slim

ARG FLAG=FLAG{default}

COPY . /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

RUN sed -i "s|PLACEHOLDER_FLAG|${FLAG}|g" controller.conf

RUN rm -f flag.txt

ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
