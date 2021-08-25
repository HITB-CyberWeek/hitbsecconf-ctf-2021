const path = require('path');
const { convert } = require('html-to-text');
const ERROR = -1;

class CommandHandler {
    #userDb;
    #emailDb;
    #attachmentDb;

    #termCols;
    #user;
    #workingDir;
    #latestReceivedDate;
    #email;

    constructor(userDb, emailDb, attachmentDb) {
        this.#userDb = userDb;
        this.#emailDb = emailDb;
        this.#attachmentDb = attachmentDb;
    }

    #commands = {
        'help': args => this.#handleHelpCommand(args),
        'adduser': async args => await this.#handleAddUserCommand(args),
        'login': async args => await this.#handleLoginUserCommand(args),
        'logout': args => this.#handleLogoutUserCommand(args),
        'ls': async args => await this.#handleLsCommand(args),
        'cd': async args => await this.#handleCdCommand(args),
        'cat': async args => await this.#handleCatCommand(args)
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
        if (!this.#user) {
            return this.#makeResponse('Available commands:\n- adduser <username> <password>\n- help\n- login <username> <password>');
        }

        return this.#makeResponse('Available commands:\n- cat <filename>\n- cd <directory>\n- help\n- logout\n- ls');
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
            return this.#makeResponse(emails.map((e, i) => {return `${i.toString()}/: [${e.received_date.toISOString()}] ${e.mail_from.original}: ${e.subject}`}).join('\n'));
        }

        if (this.#workingDir.includes('/attachments')) {
            return this.#makeResponse(this.#email.attachments.map((e, i) => {return `${e.filename}`}).join('\n'));
        }

        var files = [];
        if (this.#email.attachments && this.#email.attachments.length > 0) {
            files.push('attachments/');
        }

        if (this.#email.raw_html) {
            files.push('html');
        }

        if (this.#email.raw_text) {
            files.push('text');
        }

        return this.#makeResponse(files.join('\n'));
    }

    async #handleCdCommand(args) {
        if (!this.#user) {
            return this.#makeResponse(`${args[0]}: command not found`, ERROR);
        }

        if (args.length != 2) {
            return this.#makeResponse(`${args[0]}: invalid command arguments`, ERROR);
        }

        const normalizedPath = path.normalize(path.join(this.#workingDir, args[1]));
        if (args[1] == '/' || normalizedPath == '/') {
            this.#workingDir = '/';
            this.#email = '';
        } else {
            const emailPathRegex = /^\/(?<index>\d+)(\/attachments\/?)?$/;
            const match = normalizedPath.match(emailPathRegex);
            if (!match) {
                return this.#makeResponse(`${args[0]}: no such directory`, ERROR);
            }

            const email = await this.#emailDb.getEmail(this.#user, this.#latestReceivedDate, parseInt(match.groups.index));
            if (!email) {
                return this.#makeResponse(`${args[0]}: no such directory`, ERROR);
            }

            if (normalizedPath.includes('/attachments') && (!this.#email.attachments || !this.#email.attachments.length)) {
                return this.#makeResponse(`${args[0]}: no such directory`, ERROR);
            }

            this.#email = email;
            this.#workingDir = normalizedPath;
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

        if (!this.#workingDir.includes('/attachments')) {
            if (args[1] == 'html' && this.#email.raw_html) {
                return this.#makeResponse(convert(this.#email.raw_html.trimEnd(), {wordwrap: this.#termCols}));
            }

            if (args[1] == 'text' && this.#email.raw_text) {
                return this.#makeResponse(this.#email.raw_text.trimEnd());
            }
        } else {
            const attachments = this.#email.attachments.filter(x => x.filename == args[1]);
            if (attachments.length == 1) {
                const data = await this.#attachmentDb.readAttachmentBase64(attachments[0].cid, attachments[0].fileName);
                if (data) {
                    return this.#makeResponse(data);
                }
            }
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
