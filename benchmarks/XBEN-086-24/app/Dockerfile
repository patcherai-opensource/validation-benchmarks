FROM ruby:3.1.2

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

ARG FLAG="PLACEHOLDER_FLAG"
ENV FLAG=${FLAG}

COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

RUN rm -f /app/flag.txt

EXPOSE 4567
CMD ["/app/startup.sh"]
