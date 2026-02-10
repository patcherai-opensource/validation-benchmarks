FROM ruby:3.1.2

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

ARG FLAG="PLACEHOLDER_FLAG"
ENV FLAG=${FLAG}

RUN mkdir -p /var/secrets && chmod 700 /var/secrets

COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

EXPOSE 4567
CMD ["/app/startup.sh"]
