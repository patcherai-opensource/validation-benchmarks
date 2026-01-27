FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/pynotebook/app/requirements.txt
RUN pip install -r /var/www/pynotebook/app/requirements.txt

COPY ./pynotebook-httpd.conf /etc/apache2/sites-available/pynotebook-httpd.conf
COPY ./website/pynotebook.wsgi /var/www/pynotebook/
COPY ./website/run.py /var/www/pynotebook/
COPY ./website/app /var/www/pynotebook/app

# Create the workspace directory structure
RUN mkdir -p /workspace/notebooks
RUN mkdir -p /workspace/data
RUN mkdir -p /workspace/.secrets

# Add some example files visible to users
RUN echo "# Welcome to PyNotebook\n\nThis is your collaborative Python development environment." > /workspace/README.md
RUN echo "print('Hello, World!')" > /workspace/notebooks/example.py
RUN echo "id,name,value\n1,test,100\n2,demo,200" > /workspace/data/sample.csv

# The flag is stored in a hidden directory that SHOULD NOT be accessible
# The allow_hidden=False setting should protect this, but there's a bug...
ARG FLAG=PLACEHOLDER_FLAG
RUN echo -n $FLAG > /workspace/.secrets/token

# Set appropriate permissions
RUN chmod -R 755 /workspace
RUN chmod 644 /workspace/.secrets/token

RUN a2dissite 000-default.conf
RUN a2ensite pynotebook-httpd.conf
RUN a2enmod headers

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
