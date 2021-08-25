const crypto = require("crypto")

class UserDb {
    #users;
    constructor(db) {
        this.#users = db.collection('users');
    }

    static async #hashPassword(password) {
        return new Promise((resolve, reject) => {
            const salt = crypto.randomBytes(8).toString("hex")

            crypto.scrypt(password.toString(), salt, 64, (err, derivedKey) => {
                if (err) reject(err);
                resolve(salt + ":" + derivedKey.toString('hex'))
            });
        });
    }

    static async #verifyPassword(password, hash) {
        return new Promise((resolve, reject) => {
            const [salt, key] = hash.split(":")
            crypto.scrypt(password, salt, 64, (err, derivedKey) => {
                if (err) reject(err);
                resolve(key == derivedKey.toString('hex'))
            });
        });
    }

    async createUser(username, password) {
        const hash = await UserDb.#hashPassword(password);

        try {
            const result = await this.#users.insertOne({_id: username, password_hash: hash});
            return result.acknowledged;
        } catch(e) {
            if (e.code != 11000) {
                throw(e);
            }
            return false;
        }
    }

    async authenticateUser(username, password) {
        const user = await this.#users.findOne({_id : username});
        if (!user) {
            return false;
        }
        return await UserDb.#verifyPassword(password, user.password_hash);
    }
}

module.exports = UserDb
