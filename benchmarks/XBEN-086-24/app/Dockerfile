FROM ruby:3.1.2

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

# Accept FLAG as both build arg and environment variable
ARG FLAG="PLACEHOLDER_FLAG"
ENV FLAG=${FLAG}

# Copy and setup the startup script that writes the flag at runtime
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

EXPOSE 4567
CMD ["/app/startup.sh"]
