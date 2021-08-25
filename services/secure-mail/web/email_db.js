class EmailDb {
    #emails;
    constructor(db) {
        this.#emails = db.collection('inbox');
    }

    async createIndices() {
        await this.#emails.createIndex({ 'rcpt_to.user': 1, 'received_date' : -1 });
    }

    async getEmails(username) {
        const query = { 'rcpt_to.user': username };
        const sort = { 'received_date' : -1 };
        const projection = { _id: 0, 'mail_from.original' : 1, subject : 1, received_date : 1, size : 1 };

        return await this.#emails.find(query).sort(sort).project(projection).toArray();
    }

    async getEmail(username, latestReceivedDate, index) {
        const query = { 'rcpt_to.user': username, 'received_date' : { $lte : latestReceivedDate } };
        const sort = { 'received_date' : -1 };
        const projection = { _id: 0, 'mail_from.original' : 1, subject : 1, received_date : 1, raw_html : 1, raw_text : 1, 'attachments.contentType' : 1, 'attachments.filename' : 1, 'attachments.size' : 1, 'attachments.cid' : 1 };

        const results = await this.#emails.find(query).sort(sort).project(projection).skip(index).limit(1).toArray();
        if (results.length) {
            return results[0];
        }
    }
}

module.exports = EmailDb
