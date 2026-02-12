FROM python:3.12-slim

ARG FLAG=FLAG{default}

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Inject the flag into the controller configuration as the admin secret key
RUN sed -i "s|FLAG_PLACEHOLDER|${FLAG}|g" /app/conf/pinot-controller.conf

# Remove build artifacts that could leak the flag
RUN rm -f /app/flag.txt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "warning"]
