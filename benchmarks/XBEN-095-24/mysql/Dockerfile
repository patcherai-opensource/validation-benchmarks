FROM mysql:5.7

ARG FLAG
ENV MYSQL_ROOT_PASSWORD=password

COPY init.sql /docker-entrypoint-initdb.d/01-init.sql

RUN printf "USE wikiengine;\nINSERT INTO site_properties (prop_name, prop_value, prop_category) VALUES ('system.secret.key', '%s', 'security');\n" "${FLAG}" > /docker-entrypoint-initdb.d/02-flag.sql

EXPOSE 3306
