FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /opt/pipelineflow/data

ARG FLAG=FLAG{placeholder}
RUN echo -n "${FLAG}" > /opt/pipelineflow/data/flag_store

COPY . /app

WORKDIR /app
EXPOSE 8000

CMD ["python", "app.py"]
