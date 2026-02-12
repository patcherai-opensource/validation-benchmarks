FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=lunary_platform
ENV MYSQL_DATABASE=database

EXPOSE 3306

HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD mysqladmin ping -h localhost -u root -p$MYSQL_ROOT_PASSWORD || exit 1
