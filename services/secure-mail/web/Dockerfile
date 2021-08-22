FROM node:latest

WORKDIR /var/www
COPY ./package.json ./
RUN npm install

COPY ./index.html ./
COPY ./mailapp.js ./
COPY ./server.js ./

USER www-data
EXPOSE 8080

CMD ["node", "server.js"]
