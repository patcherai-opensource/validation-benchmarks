FROM php:7.4-apache

RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    unzip \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd
RUN a2enmod rewrite

# Configure Apache server settings
RUN echo 'ServerTokens Prod' >> /etc/apache2/conf-available/reposilite.conf \
    && echo 'ServerSignature Off' >> /etc/apache2/conf-available/reposilite.conf \
    && echo 'AllowEncodedSlashes NoDecode' >> /etc/apache2/conf-available/reposilite.conf \
    && a2enconf reposilite

COPY . /var/www/html/

WORKDIR /var/www/html/

# Create repository data directories
RUN mkdir -p /var/www/html/data/repositories/releases \
    /var/www/html/data/repositories/snapshots \
    /var/www/html/data/repositories/public \
    /var/www/html/data/docs

# Create sample artifacts and doc caches
RUN mkdir -p /var/www/html/data/docs/releases/com/example/core-utils/2.1.0/.cache/unpack \
    /var/www/html/data/docs/releases/com/example/core-utils/2.0.0/.cache/unpack \
    /var/www/html/data/docs/releases/org/apache/commons/logging/1.3.1/.cache/unpack \
    /var/www/html/data/docs/public/io/netty/netty-codec/4.1.108/.cache/unpack

# Create sample javadoc HTML files in unpacked caches
RUN echo '<html><head><title>core-utils 2.1.0 API</title></head><body><h1>com.example.core-utils 2.1.0 API Documentation</h1><p>Core utility classes for stream processing and data transformation.</p><h2>Packages</h2><ul><li>com.example.core.io</li><li>com.example.core.util</li><li>com.example.core.collections</li></ul></body></html>' > /var/www/html/data/docs/releases/com/example/core-utils/2.1.0/.cache/unpack/index.html \
    && echo 'body { font-family: sans-serif; margin: 2em; } h1 { color: #325064; }' > /var/www/html/data/docs/releases/com/example/core-utils/2.1.0/.cache/unpack/stylesheet.css \
    && echo '<html><head><title>StringHelper</title></head><body><h1>Class StringHelper</h1><p>public class StringHelper extends Object</p><h2>Method Summary</h2><table><tr><td>static String</td><td>capitalize(String input)</td></tr><tr><td>static boolean</td><td>isBlank(String input)</td></tr></table></body></html>' > /var/www/html/data/docs/releases/com/example/core-utils/2.1.0/.cache/unpack/com.example.core.util.StringHelper.html \
    && echo '<html><head><title>core-utils 2.0.0 API</title></head><body><h1>com.example.core-utils 2.0.0 API Documentation</h1><p>Core utility classes (legacy).</p></body></html>' > /var/www/html/data/docs/releases/com/example/core-utils/2.0.0/.cache/unpack/index.html \
    && echo 'body { font-family: sans-serif; margin: 2em; }' > /var/www/html/data/docs/releases/com/example/core-utils/2.0.0/.cache/unpack/stylesheet.css \
    && echo '<html><head><title>commons-logging 1.3.1 API</title></head><body><h1>org.apache.commons.logging 1.3.1</h1><p>Apache Commons Logging API documentation.</p></body></html>' > /var/www/html/data/docs/releases/org/apache/commons/logging/1.3.1/.cache/unpack/index.html \
    && echo '<html><head><title>netty-codec 4.1.108 API</title></head><body><h1>io.netty.netty-codec 4.1.108</h1><p>Netty codec framework documentation.</p></body></html>' > /var/www/html/data/docs/public/io/netty/netty-codec/4.1.108/.cache/unpack/index.html

# Create sample artifact metadata
RUN mkdir -p /var/www/html/data/repositories/releases/com/example/core-utils/2.1.0 \
    /var/www/html/data/repositories/releases/com/example/core-utils/2.0.0 \
    /var/www/html/data/repositories/releases/org/apache/commons/logging/1.3.1 \
    /var/www/html/data/repositories/public/io/netty/netty-codec/4.1.108 \
    && echo '{"groupId":"com.example","artifactId":"core-utils","version":"2.1.0","packaging":"jar"}' > /var/www/html/data/repositories/releases/com/example/core-utils/2.1.0/maven-metadata.json \
    && echo '{"groupId":"com.example","artifactId":"core-utils","version":"2.0.0","packaging":"jar"}' > /var/www/html/data/repositories/releases/com/example/core-utils/2.0.0/maven-metadata.json \
    && echo '{"groupId":"org.apache.commons","artifactId":"logging","version":"1.3.1","packaging":"jar"}' > /var/www/html/data/repositories/releases/org/apache/commons/logging/1.3.1/maven-metadata.json \
    && echo '{"groupId":"io.netty","artifactId":"netty-codec","version":"4.1.108","packaging":"jar"}' > /var/www/html/data/repositories/public/io/netty/netty-codec/4.1.108/maven-metadata.json

# Plant flag at build time in a location only reachable via path traversal
ARG FLAG
RUN mkdir -p /opt/reposilite \
    && echo "${FLAG}" > /opt/reposilite/token.config \
    && chmod 644 /opt/reposilite/token.config

RUN chown -R www-data:www-data /var/www/html/

EXPOSE 80

CMD ["apache2-foreground"]
