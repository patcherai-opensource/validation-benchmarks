FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=password

# Save the original MySQL entrypoint
RUN cp /usr/local/bin/docker-entrypoint.sh /usr/local/bin/mysql-entrypoint.sh

COPY init.sql /docker-entrypoint-initdb.d/init-template.sql
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh /usr/local/bin/mysql-entrypoint.sh

EXPOSE 3306

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["mysqld"]
