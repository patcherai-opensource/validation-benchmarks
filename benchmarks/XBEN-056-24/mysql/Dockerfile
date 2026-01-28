FROM mysql:8.4

ENV MYSQL_ROOT_PASSWORD=eventboard_db_pass
ENV MYSQL_DATABASE=eventboard_db

EXPOSE 3306

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD mysqladmin ping -h localhost --password=eventboard_db_pass -u root || exit 1
