FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=openam
ENV MYSQL_DATABASE=database

EXPOSE 3306

HEALTHCHECK --interval=10s --timeout=5s --retries=10 \
    CMD mysqladmin ping -h localhost --password=openam -u root || exit 1
