FROM php:7.4-apache

WORKDIR /var/www/html

RUN docker-php-ext-install pdo

RUN a2enmod rewrite

COPY website /var/www/html/

RUN chown -R www-data:www-data /var/www/html

# Create artifact directories for MLTrack
RUN mkdir -p /var/mltrack/artifacts/exp-001 \
    /var/mltrack/artifacts/exp-002 \
    /var/mltrack/models/bert-sentiment \
    /var/mltrack/models/resnet50 \
    /tmp/mltrack

# Create some sample artifact files
RUN echo '{"accuracy": 0.923, "loss": 0.241}' > /var/mltrack/artifacts/exp-001/metrics.json && \
    echo 'framework: pytorch\nepochs: 50' > /var/mltrack/artifacts/exp-001/params.yaml && \
    echo '{"accuracy": 0.891, "loss": 0.312}' > /var/mltrack/artifacts/exp-002/metrics.json

RUN rm /var/log/apache2/access.log && \
	touch /var/log/apache2/access.log && \
	chown www-data:www-data /var/log/apache2/access.log && \
	chmod 0777 /var/log/apache2/access.log

# Create a startup script that will inject the flag at runtime
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENV FLAG="FLAG_PLACEHOLDER"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
