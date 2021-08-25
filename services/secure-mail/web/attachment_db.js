const fs = require('fs').promises;
const path = require('path');

class AttachmentDb {
    #pathPrefix;
    constructor(pathPrefix) {
        this.#pathPrefix = pathPrefix;
    }

    async readAttachmentBase64(cid, filename) {
        const fullPath = path.join(this.#pathPrefix, cid, filename);

        try {
            return await fs.readFile(fullPath, {encoding: 'base64'});
        } catch (e) {
            return;
        }
    }
}

module.exports = AttachmentDb
