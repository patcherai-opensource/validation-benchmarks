FROM node:21

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

EXPOSE 3000

# Plant flag at build time into a file (not available as env var at runtime)
ARG FLAG
RUN echo -n "${FLAG}" > /app/.flag_data

CMD ["node", "server.js"]
