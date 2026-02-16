FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=idp_platform
ENV MYSQL_DATABASE=database

EXPOSE 3306

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD mysqladmin ping -h localhost --password=idp_platform -u root || exit 1
