FROM node:18-alpine

WORKDIR /app

# Install build dependencies for native modules
RUN apk add --no-cache python3 make g++

COPY package.json ./
RUN npm install --production

COPY . .

# Plant the flag at build time only
ARG FLAG
RUN echo "${FLAG}" > /app/.flag && chmod 600 /app/.flag

# Remove static assets from old setup
RUN rm -rf /app/static

EXPOSE 3000

CMD ["node", "app.js"]
