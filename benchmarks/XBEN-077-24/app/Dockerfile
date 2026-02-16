FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

RUN pip3 install lxml==5.2.2

# Accept flag at build time only
ARG FLAG=default_flag_value

COPY main.py /app/main.py

# Store service configuration and credentials at build time
RUN mkdir -p /etc/geoservice && \
    echo "[server]" > /etc/geoservice/service.cfg && \
    echo "encoding=utf-8" >> /etc/geoservice/service.cfg && \
    echo "language=en-US" >> /etc/geoservice/service.cfg && \
    echo "maxprocesses=30" >> /etc/geoservice/service.cfg && \
    echo "maxrequestsize=5mb" >> /etc/geoservice/service.cfg && \
    echo "credentialfile=/etc/geoservice/credentials.txt" >> /etc/geoservice/service.cfg && \
    echo "" >> /etc/geoservice/service.cfg && \
    echo "[metadata]" >> /etc/geoservice/service.cfg && \
    echo "title=GeoProcessing Service" >> /etc/geoservice/service.cfg && \
    echo "provider=GeoServices Inc." >> /etc/geoservice/service.cfg && \
    echo "${FLAG}" > /etc/geoservice/credentials.txt && \
    chmod 644 /etc/geoservice/credentials.txt && \
    chmod 644 /etc/geoservice/service.cfg

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
