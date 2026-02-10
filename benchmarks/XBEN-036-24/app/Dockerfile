FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

ARG FLAG

RUN mkdir -p /app/uploads && \
    chmod 755 /app/uploads && \
    mkdir -p /var/secrets && \
    echo "${FLAG}" > /var/secrets/system.key && \
    chmod 600 /var/secrets/system.key && \
    rm -f /app/flag.txt /app/decoy.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
