const process = require('process');
const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
const { convert } = require('html-to-text');
const { MongoClient } = require("mongodb");

const port = 8080;
const mongoClient = new MongoClient('mongodb://mongodb/emails');
// TODO change to ctf.hitb.org?
const domain = 'hackerdom.com';

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

async function get_emails(username) {
  try {
    await mongoClient.connect();
    const database = mongoClient.db('emails');
    const movies = database.collection('inbox');
    const query = { 'rcpt_to.user': username };
    const sort = { 'received_date' : -1 };
    const projection = { _id: 0, 'mail_from.original' : 1, subject : 1, received_date : 1, size : 1 };
    return await movies.find(query).sort(sort).project(projection).toArray();
  } finally {
    await mongoClient.close();
  }
}

async function get_email(username, latestReceivedDate, index) {
  try {
    await mongoClient.connect();
    const database = mongoClient.db('emails');
    const inbox = database.collection('inbox');
    const query = { 'rcpt_to.user': username, 'received_date' : { $lte : latestReceivedDate } };
    const sort = { 'received_date' : -1 };
    const projection = { _id: 0, 'mail_from.original' : 1, subject : 1, received_date : 1, html : 1, text : 1, 'attachments.contentType' : 1, 'attachments.filename' : 1, 'attachments.size' : 1, 'attachments.cid' : 1 };
    const results = await inbox.find(query).sort(sort).project(projection).limit(1).toArray();
    if (results.length) {
        return results[0];
    }
  } finally {
    await mongoClient.close();
  }
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
    ws.on('message', async command => {
        console.log(`received: >>${command}<<, ws.authUser=${ws.authUser}`);

        if (!ws.termCols) {
            ws.termCols = parseInt(command);
            return;
        }

        var response = {exit_code : 0, output : '', working_dir : ''};

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
                        ws.workingDir = '/';
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
                    delete ws.workingDir;
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
                    if (ws.workingDir == '/') {
                        // TODO use ws.workingDir
                        var emails = await get_emails(ws.authUser);
                        if (emails.length) {
                            ws.latestReceivedDate = emails[0].received_date;
                        }
                        response.output = emails.map((e, i) => {return `${i.toString()}/: [${e.received_date.toISOString()}] ${e.mail_from.original}: ${e.subject}`}).join('\r\n');
                    } else {
                        var files = [];
                        if (ws.currentEmail.attachments) {
                            files.push('attachments/');
                        }
                        if (ws.currentEmail.html) {
                            files.push('html');
                        }
                        if (ws.currentEmail.text) {
                            files.push('text');
                        }
                        response.output = files.join('\r\n');
                    }
                }
                break;
            case 'cd':
                if (!ws.authUser) {
                    response.output = `${argv[0]}: command not found`;
                    response.exit_code = -1;
                } else if (argv.length != 2) {
                    response.output = `${argv[0]}: invalid command arguments`;
                    response.exit_code = -1;
                } else {
                    if (argv[1] == '/') {
                        ws.workingDir = '/';
                    } else {
                        const normalizedPath = path.normalize(path.join(ws.workingDir, argv[1]));
                        const pathRegex = /^\/(?<index>\d+)\/?$/;
                        const match = normalizedPath.match(pathRegex);
                        if (!match) {
                            response.output = `${argv[0]}: no such directory`;
                            response.exit_code = -1;
                        } else {
                            if (match.groups.index) {
                                ws.currentEmail = await get_email(ws.authUser, ws.latestReceivedDate, parseInt(match.groups.index));
                                console.log(ws.currentEmail);
                            }
                            // TODO check path exists
                            ws.workingDir = normalizedPath;
                        }
                    }

                    if (ws.workingDir == '/') {
                        delete ws.currentEmail;
                    }
                }
                break;
            case 'cat':
                if (!ws.authUser) {
                    response.output = `${argv[0]}: command not found`;
                    response.exit_code = -1;
                } else if (argv.length != 2) {
                    response.output = `${argv[0]}: invalid command arguments`;
                    response.exit_code = -1;
                } else {
                    if (argv[1] == 'html') {
                        // TODO check exists
                        response.output = convert(ws.currentEmail.html, {wordwrap: ws.termCols}).replace(/\n/g, "\r\n");
                    } else if (argv[1] == 'text') {
                        // TODO check exists
                        response.output = ws.currentEmail.text.replace(/\n/g, "\r\n");
                    }
                }
                break;
            default:
                response.output = `${argv[0]}: command not found`;
                response.exit_code = -1;
                break;
        }
        if (ws.workingDir) {
            response.working_dir = ws.workingDir;
        }
        ws.send(JSON.stringify(response));
    });
});

server.listen(port, () => {
  console.log(`Server started`);
});
