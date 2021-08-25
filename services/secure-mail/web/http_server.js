const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
const CommandHandler = require('./command_handler.js');
const UserDb = require('./user_db.js');
const EmailDb = require('./email_db.js');
const AttachmentDb = require('./attachment_db.js');

class HttpServer {
    static #ROUTES = {
        '/' : {filePath : 'index.html', contentType : 'text/html'},
        '/xterm.css' : {filePath : 'node_modules/xterm/css/xterm.css', contentType : 'text/css'},
        '/xterm.js' : {filePath : 'node_modules/xterm/lib/xterm.js', contentType : 'text/javascript'},
        '/xterm.js.map' : {filePath : 'node_modules/xterm/lib/xterm.js.map', contentType : 'application/json'},
        '/xterm-addon-fit.js' : {filePath : 'node_modules/xterm-addon-fit/lib/xterm-addon-fit.js', contentType : 'text/javascript'},
        '/xterm-addon-fit.js.map' : {filePath : 'node_modules/xterm-addon-fit/lib/xterm-addon-fit.js.map', contentType : 'application/json'},
        '/mailapp.js' : {filePath : 'mailapp.js', contentType : 'text/javascript'}
    };

    static #requestHandler(request, response) {
        if (!(request.url in HttpServer.#ROUTES)) {
            response.writeHead(404);
            response.end();
            return;
        }

        const route = HttpServer.#ROUTES[request.url];

        fs.readFile(route.filePath, function (error, content) {
            if (error) {
                response.writeHead(500);
                response.end();
            }
            else {
                response.writeHead(200, { 'Content-Type': route.contentType });
                response.end(content, 'utf-8');
            }
        });
    }

    #db;
    #path;
    constructor(mongoDb, attachmentPath) {
        this.#db = mongoDb;
        this.#path = attachmentPath;
    }

    async start(port) {
        const self = this;
        const server = http.createServer(HttpServer.#requestHandler);
        const wsServer = new WebSocket.Server({server: server});

        const userDb = new UserDb(this.#db);
        const emailDb = new EmailDb(this.#db);
        const attachmentDb = new AttachmentDb(this.#path);
        await emailDb.createIndices();

        wsServer.on('connection', function connection(ws) {
            const handler = new CommandHandler(userDb, emailDb, attachmentDb);
            ws.on('message', async command => {
                const response = await handler.handle(command);
                if (response) {
                    ws.send(JSON.stringify(response));
                }
            });
        });

        server.listen(port, () => {
            console.log('HTTP server started');
        });
    }
}

module.exports = HttpServer
