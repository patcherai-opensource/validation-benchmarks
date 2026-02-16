FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/ssti_loan_calculator/app/requirements.txt
RUN pip install -r /var/www/ssti_loan_calculator/app/requirements.txt

COPY ./ssti_loan_calculator-httpd.conf /etc/apache2/sites-available/ssti_loan_calculator-httpd.conf
COPY ./website/ssti_loan_calculator.wsgi /var/www/ssti_loan_calculator/
COPY ./website/run.py /var/www/ssti_loan_calculator/
COPY ./website/app /var/www/ssti_loan_calculator/app

# Support runtime flag injection for Kubernetes
ARG FLAG
ENV FLAG_CONTENT=${FLAG}
# Create flag file with build-time flag if provided, otherwise use placeholder
RUN if [ -n "$FLAG" ]; then echo -n "$FLAG" > /flag; else echo -n "__FLAG_PLACEHOLDER__" > /flag; fi
RUN chmod 644 /flag

# Add script to handle runtime flag injection
COPY inject-flag.sh /usr/local/bin/inject-flag.sh
RUN chmod +x /usr/local/bin/inject-flag.sh

RUN a2dissite 000-default.conf
RUN a2ensite ssti_loan_calculator-httpd.conf
RUN a2enmod headers
RUN echo "ServerTokens Prod" >> /etc/apache2/apache2.conf

# Environment variables for database connection
ENV DB_HOST=localhost
ENV DB_USER=root
ENV DB_PASSWORD=ssti_loan_calculator
ENV DB_NAME=database

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost:80/login || exit 1

ENTRYPOINT ["/usr/local/bin/inject-flag.sh"]
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
