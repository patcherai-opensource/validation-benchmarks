FROM node:18-alpine

WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY server.js ./
COPY public ./public

EXPOSE 80

# Flag injection at runtime
ENV FLAG=""

CMD ["node", "server.js"]
