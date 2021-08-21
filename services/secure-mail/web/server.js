const process = require('process');
const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');

const port = 8080;

process.on('SIGINT', () => {
  process.exit(0);
});

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
    ws.on('message', command => {
        console.log(`received: >>${command}<<`);

        var response = {exit_code : 0, output : ''};

        switch (command.toString()) {
            case 'help':
                response.output = 'HELP';
                break;
            case 'adduser':
                response.output = 'adduser';
                break;
            case 'login':
                response.output = 'login';
                break;
            default:
                response.output = `${command}: command not found`;
                response.exit_code = -1;
                break;
        }
        ws.send(JSON.stringify(response));
    });
});

server.listen(port, () => {
  console.log(`Server started`);
});
