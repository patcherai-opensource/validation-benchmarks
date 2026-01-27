FROM node:14-alpine

RUN apk --no-cache add curl
WORKDIR /app
COPY . .
RUN npm install 

# Accept flag as build argument and create the hidden .env file
ARG FLAG="FLAG{test}"
RUN echo "# ArtVault CDN Configuration" > /app/static/.env && \
    echo "CDN_VERSION=2.1.3" >> /app/static/.env && \
    echo "API_ENDPOINT=https://api.artvault.internal" >> /app/static/.env && \
    echo "ADMIN_SECRET=${FLAG}" >> /app/static/.env && \
    echo "DEBUG_MODE=false" >> /app/static/.env

EXPOSE 8333
CMD [ "npm", "start" ]
