
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY . /app

ARG FLAG

# Support both build-time and runtime flag injection
RUN if [ -n "$FLAG" ]; then sed -i s/FLAG/$FLAG/g flag.txt; fi

# Add healthcheck
HEALTHCHECK --interval=10s --timeout=1s --retries=5 --start-period=10s \
    CMD curl -f http://localhost:80/ping || exit 1

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
