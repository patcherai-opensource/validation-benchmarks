FROM mysql:8.4

ENV MYSQL_ROOT_PASSWORD=ssti_secret_art_gallery
ENV MYSQL_DATABASE=art_db

EXPOSE 3306

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD mysqladmin ping -h localhost --password=ssti_secret_art_gallery -u root || exit 1
