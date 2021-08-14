// safelinks

const { Curl } = require('node-libcurl');
const NodeClam = require('clamscan');
const Readable = require('stream').Readable;

exports.register = function () {
    const plugin = this;

    plugin.load_config();
    plugin.init_clamscan();
    plugin.register_hook('data', 'check_links');
};

exports.load_config = function () {
    const plugin = this;

    plugin.cfg = plugin.config.get('safelinks.ini', () => {
        plugin.load_config();
    });

    const defaults = {
        clamd_port: 3310
    };

    for (const key in defaults) {
        if (plugin.cfg.main[key] === undefined) {
            plugin.cfg.main[key] = defaults[key];
        }
    }
};

exports.init_clamscan = function () {
    const plugin = this;

    plugin.ClamScan = new NodeClam().init({
        clamscan: {
            active: false
        },
        clamdscan: {
            host: plugin.cfg.main.clamd_host,
            port: plugin.cfg.main.clamd_port,
            local_fallback: false,
            path: null
        }
    });
};

exports.check_link = function(uri) {
    const plugin = this;

    return new Promise((resolve, reject) => {
        const curl = new Curl();
        curl.setOpt('URL', uri);
        curl.setOpt('FOLLOWLOCATION', true);

        curl.on('end', function (statusCode, data, headers) {
            plugin.loginfo(statusCode);
            plugin.loginfo(this.getInfo('TOTAL_TIME'));

            const rs = Readable();
            rs.push(data);
            rs.push(null);

            plugin.ClamScan.then(clamscan => {
                clamscan.scan_stream(rs, (err, result) => {
                    if (err) {
                        plugin.logerror(err);
                        return reject(err);
                    }

                    const {is_infected} = result;

                    return (is_infected ? reject(new Error('infected')) : resolve());
                });
            }).catch(err => {
                plugin.logerror(err);
                return reject(err);
            });

            this.close();
        });

        curl.on('error', function (error, errorCode) {
            plugin.logerror(error.toString());
            curl.close.bind(curl);
        });

        curl.perform();
   });
};

exports.check_links = function(next, connection) {
        const plugin = this;

        const links = ['http://example.com/'];

        Promise.all(links.map(l => plugin.check_link(l))).then(() => {
            plugin.loginfo('ALL DONE');
            // TODO call next
        }).catch(err => {
            plugin.logerror(err);
            // TODO reject
        });

	next();
};
