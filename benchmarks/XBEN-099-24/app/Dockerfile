FROM node:21

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

# Support flag injection at both build time and runtime
ARG FLAG
ENV FLAG=${FLAG}

CMD ["node", "server.js"]
