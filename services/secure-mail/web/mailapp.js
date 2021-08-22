const term = new Terminal();
const fitAddon = new FitAddon.FitAddon();
term.loadAddon(fitAddon);
term.open(document.getElementById('terminal'));
fitAddon.fit();

term.setOption('cursorBlink', true);

var currentUser = '';

term.prompt = () => {
    if (currentUser) {
        term.write(`\r\n(\x1b[1;32m${currentUser}\x1b[0m)$ `);
    } else {
        term.write('\r\n$ ');
    }
};

const ws = new WebSocket('ws://' + location.host + '/');
var connected = false;

ws.onopen = () => {
    connected = true;
    ws.send(term.cols);
    term.writeln('Welcome to SecureMail');
    term.prompt();
};


ws.onclose = e => {
    connected = false;
};

var cmd = '';
var username = '';
var password = '';
var needUsername = false;
var needPassword = false;

ws.onmessage = message => {
    var response = JSON.parse(message.data);
    if (response.output) {
        if (response.exit_code !== 0) {
            term.write(`\r\n\x1b[1;31m${response.output}\x1b[0m`);
        } else {
            term.write(`\r\n${response.output}`);
        }
    }
    if (cmd.startsWith('login') && !response.exit_code) {
        currentUser = cmd.split(' ')[1];
    } else if (cmd == 'logout' && !response.exit_code) {
        currentUser = '';
    }

    term.prompt();
    cmd = '';
};

const startEnterUsername = () => {
    needUsername = true;
    term.write(`\r\nUser: `);
};
const cleanupUsername = () => {
    needUsername = false;
    username = '';
};

const startEnterPassword = () => {
    needPassword = true;
    term.write(`\r\nPassword: `);
};
const cleanupPassword = () => {
    needPassword = false;
    password = '';
};

term.onData(e => {
    if (!connected) {
        return;
    }

    switch (e) {
        case '\r':
            if (!cmd) {
                term.prompt();
            } else if (needUsername) {
                cmd += ' ' + username;
                cleanupUsername();
                startEnterPassword();
            } else if (needPassword) {
                cmd += ' ' + password;
                cleanupPassword();
                ws.send(cmd);
            } else {
                if ((cmd.startsWith('login') || cmd.startsWith('adduser')) && cmd.split(' ').length < 3) {
                    if (cmd.split(' ').length == 1) {
                        startEnterUsername();
                    } else {
                        startEnterPassword();
                    }
                } else {
                    ws.send(cmd);
                }
            }
            break;
        case '\u0003':
            cmd = '';
            cleanupUsername();
            cleanupPassword();
            term.prompt();
            break;
        case '\u007F':
            if (needUsername) {
                if (term._core.buffer.x > 6) {
                    username = username.slice(0, -1);
                    term.write('\b \b');
                }
            } else if (needPassword) {
                if (term._core.buffer.x > 10) {
                    password = password.slice(0, -1);
                    term.write('\b \b');
                }
            } else {
                var max = 2;
                if (currentUser) {
                    max += currentUser.length + 2;
                }
                if (term._core.buffer.x > max) {
                    cmd = cmd.slice(0, -1);
                    term.write('\b \b');
                }
            }
            break;
        case '\f':
            if (!needUsername && !needPassword) {
                term.clear();
            }
            break;
        default:
            if (needUsername) {
                username += e;
            } else if (needPassword) {
                password += e;
            } else {
                cmd += e;
            }
            if (!needPassword) {
                term.write(e);
            } else {
                term.write('*');
            }
    }
});
