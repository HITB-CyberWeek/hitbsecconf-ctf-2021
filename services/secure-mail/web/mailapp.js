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

ws.onmessage = message => {
  term.write(`\r\n${message.data}`);
  term.prompt();
  cmd = '';
};

term.onData(e => {
    switch (e) {
        case '\r':
            ws.send(cmd);
            break;
        case '\u0003':
            term.prompt();
            cmd = '';
            break;
        case '\u007F':
            if (term._core.buffer.x > 2) {
                cmd = cmd.slice(0, -1);
                term.write('\b \b');
            }
            break;
        case '\f':
            term.clear();
            cmd = '';
            break;
        default:
            cmd += e;
            term.write(e);
    }
});
