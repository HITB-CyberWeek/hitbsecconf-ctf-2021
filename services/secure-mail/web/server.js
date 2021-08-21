const http = require('http');
var fs = require('fs');
var path = require('path');

const requestListener = function (request, response) {
    var filePath = '';
    var contentType = '';

    switch (request.url) {
        case '/':
            filePath = 'index.html';
            contentType = 'text/html';
            break;
        case '/xterm.css':
            filePath = 'node_modules/xterm/css/xterm.css';
            contentType = 'text/css';
            break;
        case '/xterm.js':
            filePath = 'node_modules/xterm/lib/xterm.js';
            contentType = 'text/javascript';
            break;
        default:
            response.writeHead(404);
            response.end();
            return;
    }

    fs.readFile(filePath, function (error, content) {
        if (error) {
            response.writeHead(500);
            response.end();
        }
        else {
            response.writeHead(200, { 'Content-Type': contentType });
            response.end(content, 'utf-8');
        }
    });
}

const server = http.createServer(requestListener);
server.listen(8080);
