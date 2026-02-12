
FROM python:2.7.18-slim

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y phantomjs

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null

# Set default environment variables for K8s compatibility
ENV APP_HOST=localhost
ENV APP_PORT=5000

WORKDIR /var/www/typo3

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Create necessary directories for static file serving
RUN mkdir -p static/typo3temp/assets/compressed \
    static/typo3conf/ext/bootstrap_package/Resources/Public/Css \
    static/typo3conf/ext/bootstrap_package/Resources/Public/JavaScript/Dist \
    static/fileadmin/templates/images

# Inject flag at build time into the secret store
ARG FLAG=@FLAG@
RUN echo "$FLAG" > secret.txt

ENV FLASK_APP=app.py
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000
