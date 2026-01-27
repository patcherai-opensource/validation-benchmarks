FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/docportal/app/requirements.txt
RUN pip install -r /var/www/docportal/app/requirements.txt

COPY ./docportal-httpd.conf /etc/apache2/sites-available/docportal-httpd.conf
COPY ./website/docportal.wsgi /var/www/docportal/
COPY ./website/run.py /var/www/docportal/
COPY ./website/app /var/www/docportal/app

ARG FLAG
ENV FLAG=${FLAG}
# Store flag with .html extension to make it accessible via path traversal
# (mimics express-handlebars behavior where files need valid extension)
RUN echo -n "${FLAG}" > /flag.html

RUN a2dissite 000-default.conf
RUN a2ensite docportal-httpd.conf
RUN a2enmod headers

# Expose port 80
EXPOSE 80

# Create entrypoint script to handle flag injection at runtime
RUN echo '#!/bin/bash\nif [ ! -z "$FLAG" ]; then\n  echo -n "$FLAG" > /flag.html\nfi\nexec /usr/sbin/apache2ctl -D FOREGROUND' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
