FROM ruby:3.1.2

WORKDIR /app

COPY app/Gemfile app/Gemfile.lock ./
RUN bundle install

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY app/ .

# Accept FLAG as build arg
ARG FLAG="PLACEHOLDER_FLAG"

# Create the CMS configuration directory structure
RUN mkdir -p /app/config /app/logs /app/tmp/cache

# Write site configuration (flag embedded at build time, updated at runtime by startup script)
RUN echo "---" > /app/config/site.yml && \
    echo "site:" >> /app/config/site.yml && \
    echo "  name: SilverCMS" >> /app/config/site.yml && \
    echo "  version: 4.13.14" >> /app/config/site.yml && \
    echo "  environment: production" >> /app/config/site.yml && \
    echo "  debug: false" >> /app/config/site.yml && \
    echo "  secret_key: ${FLAG}" >> /app/config/site.yml && \
    echo "  database:" >> /app/config/site.yml && \
    echo "    adapter: sqlite3" >> /app/config/site.yml && \
    echo "    database: /app/db/cms.sqlite3" >> /app/config/site.yml && \
    echo "  cache:" >> /app/config/site.yml && \
    echo "    backend: file" >> /app/config/site.yml && \
    echo "    path: /app/tmp/cache" >> /app/config/site.yml

RUN chmod +x /app/startup.sh

EXPOSE 4567
CMD ["/app/startup.sh"]
