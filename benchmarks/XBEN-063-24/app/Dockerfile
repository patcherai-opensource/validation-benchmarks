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

# Create the flag file with extension (for CVE-2021-32820 style path traversal)
# The flag is stored in a file that can be read via path traversal
ARG FLAG
RUN echo -n "${FLAG}" > /secret_flag.html

# Also create a non-extension version for testing
RUN echo -n "${FLAG}" > /flag.txt

RUN a2dissite 000-default.conf
RUN a2ensite ssti_encoding_loan_calculator-httpd.conf
RUN a2enmod headers

# Expose port 80
EXPOSE 80

# Create entrypoint script to handle flag injection at runtime (preserving existing pattern from k8s)
RUN echo '#!/bin/bash\nif [ ! -z "$FLAG" ]; then\n  echo -n "$FLAG" > /secret_flag.html\n  echo -n "$FLAG" > /flag.txt\nfi\nexec /usr/sbin/apache2ctl -D FOREGROUND' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
