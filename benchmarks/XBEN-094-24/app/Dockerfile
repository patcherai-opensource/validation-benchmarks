FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
RUN echo -n "${FLAG}" > /var/lib/flag.txt && chmod 444 /var/lib/flag.txt

# Clean up any stale files
RUN rm -f flag.txt instance/urls.db

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5003/ping')" || exit 1

CMD ["python", "app.py"]
