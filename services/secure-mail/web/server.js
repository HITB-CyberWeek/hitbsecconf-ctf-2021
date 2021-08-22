const process = require('process');
const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
const { convert } = require('html-to-text');

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
        '/xterm-addon-fit.js' : {filePath : 'node_modules/xterm-addon-fit/lib/xterm-addon-fit.js', contentType : 'text/javascript'},
        '/xterm-addon-fit.js.map' : {filePath : 'node_modules/xterm-addon-fit/lib/xterm-addon-fit.js.map', contentType : 'application/json'},
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

var users = {};
const createUser = (username, password) => {
    if (username in users) {
        return false;
    }
    users[username] = password;
    return true;
};

const authenticateUser = (username, password) => {
    if (!(username in users)) {
        return false;
    }
    return users[username] == password;
};

const server = http.createServer(requestListener);
const wsServer = new WebSocket.Server({server: server});
wsServer.on('connection', function connection(ws) {
    ws.on('message', command => {
        console.log(`received: >>${command}<<, ws.authUser=${ws.authUser}`);

        if (!ws.termCols) {
            ws.termCols = parseInt(command);
            return;
        }

        var response = {exit_code : 0, output : ''};

        const argv = command.toString().split(' ').filter(function(i){return i});
        switch (argv[0]) {
            case 'help':
                response.output = 'HELP';
                break;
            case 'adduser':
                if (ws.authUser) {
                    response.output = `${argv[0]}: command not found`;
                    response.exit_code = -1;
                } else if (argv.length != 3) {
                    response.output = `${argv[0]}: invalid command arguments`;
                    response.exit_code = -1;
                } else {
                    if (createUser(argv[1], [argv[2]])) {
                        response.output = `User ${argv[1]} created`;
                    } else {
                        response.output = `${argv[0]}: user ${argv[1]} already exists`
                        response.exit_code = -1;
                    }
                }
                break;
            case 'login':
                if (ws.authUser) {
                    response.output = `${argv[0]}: command not found`;
                    response.exit_code = -1;
                } else if (argv.length != 3) {
                    response.output = `${argv[0]}: invalid command arguments`;
                    response.exit_code = -1;
                } else {
                    if (!authenticateUser(argv[1], argv[2])) {
                        response.output = `${argv[0]}: authentication failed`
                        response.exit_code = -1;
                    } else {
                        ws.authUser = argv[1];
                    }
                }
                break;
            case 'logout':
                if (!ws.authUser) {
                    response.output = `${argv[0]}: command not found`;
                    response.exit_code = -1;
                } else if (argv.length != 1) {
                    response.output = `${argv[0]}: invalid command arguments`;
                    response.exit_code = -1;
                } else {
                    delete ws.authUser;
                }
                break;
            case 'ls':
                if (!ws.authUser) {
                    response.output = `${argv[0]}: command not found`;
                    response.exit_code = -1;
                } else if (argv.length != 1) {
                    response.output = `${argv[0]}: invalid command arguments`;
                    response.exit_code = -1;
                } else {
                    const emails = ["Elon Musk <Elon.Musk@tesla.com>\tInteresting business proposal\t2021-08-21T18:35:51.348Z", 'bbb.eml'];
                    response.output = emails.join('\r\n');
                }
                break;
            case 'cat':
                if (!ws.authUser) {
                    response.output = `${argv[0]}: command not found`;
                    response.exit_code = -1;
                } else {
                    const html = "<html>\n  <body>\n    <p>Dear Sir/Madam,<br>\n       I have an <a href=\"http://www.realpython.com\">interesting business proposal</a> I want to share with you.<br><br>\n       ---<br>\n       Elon Musk\n    </p>\n  </body>\n</html>";
                    response.output = convert(html, {wordwrap: ws.termCols}).replace(/\n/g, "\r\n");
                }
                break;
            default:
                response.output = `${argv[0]}: command not found`;
                response.exit_code = -1;
                break;
        }
        ws.send(JSON.stringify(response));
    });
});

server.listen(port, () => {
  console.log(`Server started`);
});
