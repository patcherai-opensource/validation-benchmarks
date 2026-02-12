FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ARG FLAG=""
RUN if [ -n "$FLAG" ]; then echo "$FLAG" > /flag.txt; fi
RUN chmod 444 /flag.txt 2>/dev/null || true

EXPOSE 5000

CMD ["python", "app.py"]
