FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/ssti_include_loan_calculator/app/requirements.txt
RUN pip install -r /var/www/ssti_include_loan_calculator/app/requirements.txt

COPY ./ssti_include_loan_calculator-httpd.conf /etc/apache2/sites-available/ssti_include_loan_calculator-httpd.conf
COPY ./website/ssti_include_loan_calculator.wsgi /var/www/ssti_include_loan_calculator/
COPY ./website/run.py /var/www/ssti_include_loan_calculator/
COPY ./website/app /var/www/ssti_include_loan_calculator/app

ARG FLAG="PLACEHOLDER_FLAG"
# Write flag at build time for local docker-compose testing
RUN echo -n $FLAG > /flag

RUN chown -R www-data:www-data /var/www/ssti_include_loan_calculator/
RUN chmod -R 755 /var/www/ssti_include_loan_calculator/

RUN a2dissite 000-default.conf
RUN a2ensite ssti_include_loan_calculator-httpd.conf
RUN a2enmod headers

# Create entrypoint script that writes FLAG env var to file at runtime (for k8s)
# This ensures the flag is available when deployed with runtime env vars
RUN echo '#!/bin/bash\nif [ -n "$FLAG" ]; then echo -n "$FLAG" > /flag; fi\nexec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
