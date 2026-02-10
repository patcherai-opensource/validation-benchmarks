FROM node:18-alpine

ARG DEBIAN_FRONTEND=noninteractive
ARG FLAG

# Install curl for healthchecks
RUN apk add --no-cache curl

WORKDIR /app

# Copy package files and server code
COPY package.json /app/
COPY server.js /app/

# Install dependencies
RUN npm install

# Create the web root directory
RUN mkdir -p /app/public

# Copy website files to public directory
COPY website /app/public/

# Plant the flag at build time in a location outside the web root
RUN echo -n "$FLAG" > /FLAG.txt && chmod 644 /FLAG.txt

EXPOSE 80

CMD ["node", "server.js"]
