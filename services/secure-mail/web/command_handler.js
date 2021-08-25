const path = require('path');
const { convert } = require('html-to-text');
const ERROR = -1;

class CommandHandler {
    #userDb;
    #emailDb;

    #termCols;
    #user;
    #workingDir;
    #latestReceivedDate;
    #email;

    constructor(userDb, emailDb) {
        this.#userDb = userDb;
        this.#emailDb = emailDb;
    }

    #commands = {
        'help': args => this.#handleHelpCommand(args),
        'adduser': async args => await this.#handleAddUserCommand(args),
        'login': async args => await this.#handleLoginUserCommand(args),
        'logout': args => this.#handleLogoutUserCommand(args),
        'ls': async args => await this.#handleLsCommand(args),
        'cd': async args => await this.#handleCdCommand(args),
        'cat': args => this.#handleCatCommand(args)
    };

    #readTermSettings(command) {
        this.#termCols = parseInt(command);
    }

    #makeResponse(output = '', exitCode = 0) {
        var result = {exit_code : exitCode, output : output, working_dir : ''};
        if (this.#workingDir) {
            result.working_dir = this.#workingDir;
        }
        return result;
    }

    #handleHelpCommand(args) {
        return this.#makeResponse('HELP');
    }

    async #handleAddUserCommand(args) {
        if (this.#user) {
            return this.#makeResponse(`${args[0]}: command not found`, ERROR);
        }

        if (args.length != 3) {
            return this.#makeResponse(`${args[0]}: invalid command arguments`, ERROR);
        }

        var result = await this.#userDb.createUser(args[1], args[2]);
        if (result) {
            return this.#makeResponse(`User '${args[1]}' created`);
        }
        return this.#makeResponse(`${args[0]}: user '${args[1]}' already exists`, ERROR);
    }

    async #handleLoginUserCommand(args) {
        if (this.#user) {
            return this.#makeResponse(`${args[0]}: command not found`, ERROR);
        }

        if (args.length != 3) {
            return this.#makeResponse(`${args[0]}: invalid command arguments`, ERROR);
        }

        var result = await this.#userDb.authenticateUser(args[1], args[2]);
        if (!result) {
            return this.#makeResponse(`${args[0]}: authentication failed`, ERROR);
        }

        this.#user = args[1];
        this.#workingDir = '/';

        return this.#makeResponse();
    }

    async #handleLogoutUserCommand(args) {
        if (!this.#user) {
            return this.#makeResponse(`${args[0]}: command not found`, ERROR);
        }

        if (args.length != 1) {
            return this.#makeResponse(`${args[0]}: invalid command arguments`, ERROR);
        }

        this.#user = '';
        this.#workingDir = '';

        return this.#makeResponse();
    }

    async #handleLsCommand(args) {
        if (!this.#user) {
            return this.#makeResponse(`${args[0]}: command not found`, ERROR);
        }

        if (args.length != 1) {
            return this.#makeResponse(`${args[0]}: invalid command arguments`, ERROR);
        }

        if (this.#workingDir == '/') {
            var emails = await this.#emailDb.getEmails(this.#user);
            if (emails.length) {
                this.#latestReceivedDate = emails[0].received_date;
            }
            return this.#makeResponse(emails.map((e, i) => {return `${i.toString()}/: [${e.received_date.toISOString()}] ${e.mail_from.original}: ${e.subject}`}).join('\r\n'));
        }

        var files = [];
        if (this.#email.attachments) {
            files.push('attachments/');
        }

        if (this.#email.raw_html) {
            files.push('html');
        }

        if (this.#email.raw_text) {
            files.push('text');
        }

        return this.#makeResponse(files.join('\r\n'));
    }

    async #handleCdCommand(args) {
        if (!this.#user) {
            return this.#makeResponse(`${args[0]}: command not found`, ERROR);
        }

        if (args.length != 2) {
            return this.#makeResponse(`${args[0]}: invalid command arguments`, ERROR);
        }

        const dir = args[1];
        if (dir == '/') {
            this.#workingDir = '/';
        } else {
            const normalizedPath = path.normalize(path.join(this.#workingDir, dir));

            const pathRegex = /^\/(?<index>\d+)\/?$/;
            const match = normalizedPath.match(pathRegex);
            if (!match) {
                return this.#makeResponse(`${args[0]}: no such directory`, ERROR);
            }

            if (match.groups.index) {
                this.#email = await this.#emailDb.getEmail(this.#user, this.#latestReceivedDate, parseInt(match.groups.index));
            }
            // TODO check path exists
            this.#workingDir = normalizedPath;
        }

        if (this.#workingDir == '/') {
            this.#email = '';
        }

        return this.#makeResponse();
    }

    async #handleCatCommand(args) {
        if (!this.#user) {
            return this.#makeResponse(`${args[0]}: command not found`, ERROR);
        }

        if (args.length != 2) {
            return this.#makeResponse(`${args[0]}: invalid command arguments`, ERROR);
        }

        if (args[1] == 'html' && this.#email.raw_html) {
            return this.#makeResponse(convert(this.#email.raw_html, {wordwrap: this.#termCols}).replace(/\n/g, "\r\n"));
        }

        if (args[1] == 'text' && this.#email.raw_text) {
            return this.#makeResponse(this.#email.raw_text.replace(/\n/g, "\r\n"));
        }

        return this.#makeResponse(`${args[0]}: no such file or directory`, ERROR);
    }

    handle(command) {
        if (!this.#termCols) {
            this.#readTermSettings(command);
            return;
        }

        const args = command.toString().split(' ').filter(function(i){return i});
        if (!(args[0] in this.#commands)) {
            return this.#makeResponse(`${args[0]}: command not found`, ERROR);
        } else {
            return this.#commands[args[0]](args);
        }
    }
}

module.exports = CommandHandler;
