FROM python:2.7.18-slim

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

# Environment variables for K8s compatibility
ENV APP_HOST=localhost
ENV APP_PORT=5000
ENV FLASK_APP=app.py

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ARG FLAG

RUN sed -i s/@FLAG@/$FLAG/g secret.txt

# Add health check - we can't use curl in this image, so using TCP check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD timeout 10s bash -c ':> /dev/tcp/127.0.0.1/5000' || exit 1

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000
