const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');

const requestListener = function (request, response) {
    const routes = {
        '/' : {filePath : 'index.html', contentType : 'text/html'},
        '/xterm.css' : {filePath : 'node_modules/xterm/css/xterm.css', contentType : 'text/css'},
        '/xterm.js' : {filePath : 'node_modules/xterm/lib/xterm.js', contentType : 'text/javascript'},
        '/xterm.js.map' : {filePath : 'node_modules/xterm/lib/xterm.js.map', contentType : 'application/json'},
        '/mailapp.js' : {filePath : 'mailapp.js', contentType : 'text/javascript'}
    };

    if (!(request.url in routes)) {
        response.writeHead(404);
        response.end();
        return;
    }

    const route = routes[request.url];
 
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

const server = http.createServer(requestListener);
const wsServer = new WebSocket.Server({server: server});
wsServer.on('connection', function connection(ws) {
    console.log(`Connection`);

    ws.on('message', function incoming(message) {
        console.log(`received: ${message}`);
        ws.send("OUTPUT");
    });
});

server.listen(8080);
