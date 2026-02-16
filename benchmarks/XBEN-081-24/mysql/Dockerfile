FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=password

# Copy init script
COPY init.sql /docker-entrypoint-initdb.d/init.sql
COPY docker-entrypoint.sh /usr/local/bin/custom-entrypoint.sh

# Make the custom entrypoint executable
RUN chmod +x /usr/local/bin/custom-entrypoint.sh

EXPOSE 3306

ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]
CMD ["mysqld"]
