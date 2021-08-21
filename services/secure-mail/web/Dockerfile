FROM node:latest

WORKDIR /var/www
COPY ./index.html ./
COPY ./mailapp.js ./
COPY ./package.json ./
COPY ./server.js ./

RUN npm install

USER www-data
EXPOSE 8080

CMD ["node", "server.js"]
