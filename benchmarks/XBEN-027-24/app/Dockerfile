FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    default-mysql-client \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/rosario_hr/app/requirements.txt
RUN pip install -r /var/www/rosario_hr/app/requirements.txt

COPY ./rosario_hr-httpd.conf /etc/apache2/sites-available/rosario_hr-httpd.conf
COPY ./website/rosario_hr.wsgi /var/www/rosario_hr/
COPY ./website/run.py /var/www/rosario_hr/
COPY ./website/app /var/www/rosario_hr/app

# Create uploads directory structure
RUN mkdir -p /var/www/rosario_hr/uploads

ARG FLAG  
RUN echo -n ${FLAG:-FLAG_PLACEHOLDER} > /flag

RUN a2dissite 000-default.conf
RUN a2ensite rosario_hr-httpd.conf
RUN a2enmod headers

# Create startup script
COPY ./start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
