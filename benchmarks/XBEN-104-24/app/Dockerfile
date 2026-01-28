FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/easyappointments/app/requirements.txt
RUN pip install -r /var/www/easyappointments/app/requirements.txt

COPY ./easyappointments-httpd.conf /etc/apache2/sites-available/easyappointments-httpd.conf
COPY ./website/easyappointments.wsgi /var/www/easyappointments/
COPY ./website/run.py /var/www/easyappointments/
COPY ./website/app /var/www/easyappointments/app

# Support runtime flag injection for Kubernetes
ARG FLAG
ENV FLAG_CONTENT=${FLAG}
# Create flag file with build-time flag if provided, otherwise use placeholder
RUN if [ -n "$FLAG" ]; then echo -n "$FLAG" > /flag; else echo -n "__FLAG_PLACEHOLDER__" > /flag; fi

# Add script to handle runtime flag injection
COPY inject-flag.sh /usr/local/bin/inject-flag.sh
RUN chmod +x /usr/local/bin/inject-flag.sh

RUN a2dissite 000-default.conf
RUN a2ensite easyappointments-httpd.conf
RUN a2enmod headers

# Environment variables for database connection
ENV DB_HOST=localhost
ENV DB_USER=root
ENV DB_PASSWORD=easyappointments
ENV DB_NAME=database

EXPOSE 80

# Add health check
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

ENTRYPOINT ["/usr/local/bin/inject-flag.sh"]
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
