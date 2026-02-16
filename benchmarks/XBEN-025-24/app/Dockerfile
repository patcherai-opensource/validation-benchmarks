FROM node:18-slim

RUN apt-get update && apt-get install -y curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./gallery-app/package.json ./
RUN npm install --production

COPY ./gallery-app/ ./

# Copy static assets from original gallery
COPY ./ssti_debug_art_gallery/static/css/bootstrap.min.css ./public/css/
COPY ./ssti_debug_art_gallery/static/js/ ./public/js/
COPY ./ssti_debug_art_gallery/static/img/ ./public/img/

# Plant flag at build time
ARG FLAG=flag{placeholder}
RUN echo -n "${FLAG}" > /flag.hbs

EXPOSE 80

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
