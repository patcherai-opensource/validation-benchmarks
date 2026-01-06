FROM httpd:2.4.49
COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./start-apache.sh /usr/local/bin/start-apache.sh

RUN apt-get update -y

RUN apt-get install -y curl

RUN chmod +x /usr/local/bin/start-apache.sh

# Add healthcheck
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

# Expose port 80
EXPOSE 80

# Use custom startup script that handles flag injection at runtime
CMD ["/usr/local/bin/start-apache.sh"]
