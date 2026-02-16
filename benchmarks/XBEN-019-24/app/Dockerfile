FROM debian:bullseye-slim

ARG FLAG="FLAG{default_flag_placeholder}"

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/vaultkeeper/requirements.txt
RUN pip install -r /var/www/vaultkeeper/requirements.txt

# Copy Apache config
COPY ./vaultkeeper-httpd.conf /etc/apache2/sites-available/vaultkeeper-httpd.conf

# Copy WSGI entry
COPY ./website/vaultkeeper.wsgi /var/www/vaultkeeper/

# Copy Flask app
COPY ./website/run.py /var/www/vaultkeeper/
COPY ./website/app /var/www/vaultkeeper/app

# Build the application directory structure (mirroring a password manager)
# These directories contain various application components

# --- svc/Handler/ directory (API handlers - has index.html) ---
RUN mkdir -p /var/www/vaultkeeper/svc/Handler
COPY ./appdata/svc/Handler/ /var/www/vaultkeeper/svc/Handler/

# --- svc/Schema/ directory (data models - NO index.html -> directory listing) ---
RUN mkdir -p /var/www/vaultkeeper/svc/Schema
COPY ./appdata/svc/Schema/ /var/www/vaultkeeper/svc/Schema/

# --- svc/lib/ directory (shared libs - has index.html) ---
RUN mkdir -p /var/www/vaultkeeper/svc/lib
COPY ./appdata/svc/lib/ /var/www/vaultkeeper/svc/lib/

# --- config/ directory (configuration - NO index.html -> directory listing) ---
RUN mkdir -p /var/www/vaultkeeper/config
COPY ./appdata/config/ /var/www/vaultkeeper/config/

# --- modules/ directory (feature modules - has index.html) ---
RUN mkdir -p /var/www/vaultkeeper/modules
COPY ./appdata/modules/ /var/www/vaultkeeper/modules/

# --- resources/ directory (scripts/tasks - NO index.html -> directory listing) ---
RUN mkdir -p /var/www/vaultkeeper/resources
COPY ./appdata/resources/ /var/www/vaultkeeper/resources/

# --- data/ directory (uploads/files - has index.html) ---
RUN mkdir -p /var/www/vaultkeeper/data
COPY ./appdata/data/ /var/www/vaultkeeper/data/

# --- handlers/ directory (source query handlers - NO index.html) ---
RUN mkdir -p /var/www/vaultkeeper/handlers
COPY ./appdata/handlers/ /var/www/vaultkeeper/handlers/

# Inject flag into the database connection settings file at build time
RUN sed -i "s|__FLAG_PLACEHOLDER__|${FLAG}|g" /var/www/vaultkeeper/config/db_settings.py

# Set proper permissions
RUN chown -R www-data:www-data /var/www/vaultkeeper

RUN a2dissite 000-default.conf
RUN a2ensite vaultkeeper-httpd.conf
RUN a2enmod headers

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
