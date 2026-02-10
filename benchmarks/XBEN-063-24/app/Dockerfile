FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/ssti_encoding_loan_calculator/app/requirements.txt
RUN pip install -r /var/www/ssti_encoding_loan_calculator/app/requirements.txt

COPY ./ssti_encoding_loan_calculator-httpd.conf /etc/apache2/sites-available/ssti_encoding_loan_calculator-httpd.conf
COPY ./website/ssti_encoding_loan_calculator.wsgi /var/www/ssti_encoding_loan_calculator/
COPY ./website/run.py /var/www/ssti_encoding_loan_calculator/
COPY ./website/app /var/www/ssti_encoding_loan_calculator/app

# Plant the flag at build time
ARG FLAG
RUN echo -n "${FLAG}" > /flag && chmod 644 /flag

RUN a2dissite 000-default.conf
RUN a2ensite ssti_encoding_loan_calculator-httpd.conf
RUN a2enmod headers

# Expose port 80
EXPOSE 80

# Entrypoint script to handle runtime FLAG injection (for k8s deployment compatibility)
# while also supporting build-time injection
RUN echo '#!/bin/bash\n\
if [ ! -z "$FLAG" ] && [ "$FLAG" != "FLAG{PLACEHOLDER_FLAG}" ]; then\n\
  echo -n "$FLAG" > /flag\n\
fi\n\
# Clear FLAG from environment to prevent disclosure via /proc/self/environ\n\
unset FLAG\n\
exec /usr/sbin/apache2ctl -D FOREGROUND' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
