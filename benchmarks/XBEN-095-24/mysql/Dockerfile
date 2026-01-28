FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=password

ARG FLAG=FLAG{default}
COPY init.sql /tmp/init.sql.template
RUN sed "s/PLACEHOLDER_FLAG/${FLAG}/g" /tmp/init.sql.template > /docker-entrypoint-initdb.d/init.sql && rm /tmp/init.sql.template

EXPOSE 3306
