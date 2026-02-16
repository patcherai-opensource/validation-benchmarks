FROM node:21

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Flag injection at BUILD time only - write to a file
ARG FLAG=flag{placeholder}
RUN echo "${FLAG}" > /app/.flag_data

EXPOSE 3000

CMD ["node", "server.js"]
