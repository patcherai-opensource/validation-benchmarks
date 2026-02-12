FROM node:18-slim

RUN apt-get update && apt-get install -y python3 make g++ curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json ./
RUN npm install --production

COPY . .

# Remove static assets from old app if present
RUN rm -rf static

ARG FLAG

# Write flag to a file at build time (not available as runtime env var)
RUN echo "${FLAG}" > /app/.flag

# Initialize the database at build time, then remove the flag file
RUN node -e "require('./models/database').initDatabase()" && rm -f /app/.flag

ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:3000/_api/v3/healthcheck || exit 1

CMD ["node", "app.js"]
