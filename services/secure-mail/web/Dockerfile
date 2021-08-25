FROM node:latest

WORKDIR /var/www
COPY ./package.json ./
RUN npm install

COPY ./index.html ./
COPY ./mailapp.js ./
COPY ./server.js ./
COPY ./http_server.js ./
COPY ./command_handler.js ./
COPY ./user_db.js ./
COPY ./email_db.js ./
COPY ./attachment_db.js ./

USER www-data
EXPOSE 8080

CMD ["node", "server.js"]
