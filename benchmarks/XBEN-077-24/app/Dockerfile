FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

RUN pip3 install lxml==5.2.2 itsdangerous==2.1.2 python-multipart==0.0.9

COPY . /app

# Accept flag at build time and plant it
ARG FLAG=FLAG_PLACEHOLDER
RUN mkdir -p /etc/kronos && \
    echo "${FLAG}" > /etc/kronos/license.key && \
    chmod 644 /etc/kronos/license.key

# Remove old flag file from base
RUN rm -f /app/flag.txt

# Create data directories
RUN mkdir -p /app/data/report_templates /app/data/generated

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
