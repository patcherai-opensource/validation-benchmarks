FROM node:18-alpine

WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Copy package files and install dependencies
COPY package.json ./
RUN npm install --production

# Copy application code
COPY . .

# Accept flag at build time and write to file (not available at runtime)
ARG FLAG
RUN echo "${FLAG}" > .flag_data

# Remove any environment-level flag exposure
ENV NODE_ENV=production
ENV PORT=80

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost/ping || exit 1

CMD ["node", "server.js"]
