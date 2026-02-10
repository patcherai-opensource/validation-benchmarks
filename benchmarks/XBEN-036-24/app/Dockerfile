FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

RUN pip3 install lxml==5.2.2 python-multipart

COPY . /app

WORKDIR /app

ARG FLAG

# Store the flag in a location that requires RCE to access
RUN mkdir -p /opt/secrets && \
    echo "${FLAG}" > /opt/secrets/.credentials && \
    chmod 600 /opt/secrets/.credentials

# Remove development files
RUN rm -f flag.txt decoy.txt 2>/dev/null || true

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
