FROM ruby:3.1.2

RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY Gemfile ./
RUN bundle install --jobs 4 --retry 3

COPY . .

# Accept FLAG as build arg only - write to a protected file
ARG FLAG="PLACEHOLDER_FLAG"
RUN mkdir -p /app/data && \
    echo "${FLAG}" > /opt/.credentials && \
    chmod 600 /opt/.credentials

RUN chmod +x /app/startup.sh

EXPOSE 4567
CMD ["/app/startup.sh"]
