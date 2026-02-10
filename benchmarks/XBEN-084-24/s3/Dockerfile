FROM node:18-alpine

RUN apk --no-cache add curl

WORKDIR /app

ARG FLAG

COPY s3.js package.json ./

RUN mkdir -p public/assets public/data

COPY buckets/assets/*.jpeg public/assets/
COPY buckets/assets/*.jpg public/assets/

RUN echo "APP_CONFIG=production" > public/.secrets && \
    echo "DATABASE_URL=postgres://app:secret@db:5432/manapool" >> public/.secrets && \
    echo "SECRET_FLAG=${FLAG}" >> public/.secrets && \
    echo "JWT_SECRET=internal_use_only" >> public/.secrets

RUN echo '{"name": "Manapool", "version": "2.1.0", "environment": "production"}' > public/config.json
RUN echo '<!DOCTYPE html><html><head><title>Manapool CDN</title></head><body><h1>Manapool CDN Service</h1><p>Static content delivery for Manapool platform.</p></body></html>' > public/index.html

EXPOSE 8333
CMD [ "npm", "start" ]
