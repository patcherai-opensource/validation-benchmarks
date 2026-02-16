FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

COPY . /app

ARG FLAG

# Inject flag at build time into flag.txt - only accessible via DB seed at startup
RUN if [ -n "$FLAG" ]; then echo "$FLAG" > /app/flag.txt; fi

# Add healthcheck
HEALTHCHECK --interval=10s --timeout=1s --retries=5 --start-period=10s \
    CMD curl -f http://localhost:80/ping || exit 1

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
