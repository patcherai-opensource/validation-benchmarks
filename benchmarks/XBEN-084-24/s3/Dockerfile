FROM node:18-alpine

RUN apk --no-cache add curl

WORKDIR /app

# Copy application files
COPY package*.json ./
COPY s3.js ./

# Create static directory structure
RUN mkdir -p static/public static/assets

# Copy some placeholder content for public directory
RUN echo '{"message": "Welcome to the static file server", "endpoints": ["/public/", "/assets/"]}' > static/public/index.json
RUN echo 'This is a sample text file in the public directory.' > static/public/readme.txt

# Copy assets (images and other files will go here)
RUN echo '{"type": "assets", "description": "Asset storage directory"}' > static/assets/info.json

# Accept FLAG as build argument and create hidden .env file in static root
ARG FLAG
RUN echo "# Application Configuration" > static/.env && \
    echo "APP_SECRET=xK9mP2nQ7wE4rT1y" >> static/.env && \
    echo "DATABASE_URL=postgres://localhost:5432/app" >> static/.env && \
    echo "FLAG=${FLAG}" >> static/.env && \
    echo "DEBUG=false" >> static/.env

# Also create a hidden config directory with some sensitive data
RUN mkdir -p static/.config && \
    echo '{"api_key": "sk-demo-12345", "note": "Check .env for the flag"}' > static/.config/settings.json

EXPOSE 8333
CMD [ "node", "s3.js" ]
