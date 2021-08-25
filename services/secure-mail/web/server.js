const process = require('process');
const { MongoClient } = require("mongodb");
const HttpServer = require('./http_server.js');
const UserDb = require('./user_db.js');

const PORT = 8080;
const MONGO_URI = 'mongodb://mongodb/emails';

process.on('SIGINT', () => {
    process.exit(0);
});

const mongoClient = new MongoClient(MONGO_URI);
(async () => {
    await mongoClient.connect();
    const mongoDb = mongoClient.db();

    const server = new HttpServer(mongoDb);
    await server.start(PORT);
})();
