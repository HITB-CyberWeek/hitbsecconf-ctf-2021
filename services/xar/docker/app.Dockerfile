FROM node:16-alpine

USER node
RUN mkdir /home/node/app
WORKDIR /home/node/app

COPY --chown=node:node package.json /home/node/app/package.json
RUN yarn install

COPY --chown=node:node . /home/node/app
RUN yarn run tsoa spec-and-routes && yarn run tsc --outDir build

ENTRYPOINT ["node", "build/src/server.js"]
