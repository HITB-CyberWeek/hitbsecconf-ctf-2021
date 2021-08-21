const term = new Terminal();
term.setOption('cursorBlink', true);
term.open(document.getElementById('terminal'));
term.prompt = () => {
    term.write('\r\n$ ');
};

const ws = new WebSocket('ws://' + location.host + '/');

ws.onopen = () => {
    term.writeln('Welcome to SecureMail');
    term.prompt();
};

var cmd = '';
var username = '';
var password = '';
var needUsername = false;
var needPassword = false;

// TODO: message: {exit_code: ..., output: ...}

ws.onmessage = message => {
  term.write(`\r\n${message.data}`);
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
    switch (e) {
        case '\r':
            if (needUsername) {
                cmd += ' ' + username;
                cleanupUsername();
                startEnterPassword();
            } else if (needPassword) {
                cmd += ' ' + password;
                cleanupPassword();
                ws.send(cmd);
            } else {
                if ((cmd.startsWith('login') || cmd.startsWith('adduser')) && cmd.split(' ').length != 3) {
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
            if (term._core.buffer.x > 2) {
                if (needUsername) {
                    username = username.slice(0, -1);
                } else if (needPassword) {
                    password = password.slice(0, -1);
                } else {
                    cmd = cmd.slice(0, -1);
                }
                term.write('\b \b');
            }
            break;
        case '\f':
            if (!needUsername && !needPassword) {
                term.clear();
                cmd = '';
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
