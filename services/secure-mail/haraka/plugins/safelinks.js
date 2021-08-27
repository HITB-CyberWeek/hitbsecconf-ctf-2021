const { Curl } = require('node-libcurl');
const NodeClam = require('clamscan');
const Readable = require('stream').Readable;
const libmime = require('libmime');
const cheerio = require('cheerio');

exports.register = function () {
    const plugin = this;

    plugin.load_config();
    plugin.init_clamscan();
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

exports.extract_links_from_html = function (html) {
    const $ = cheerio.load(html);

    var result = new Array();
    $('a').each(function(i, link) {
        result.push($(link).attr('href'));
    });
    return result;
};

exports.check_link = function (uri) {
    const plugin = this;

    return new Promise((resolve, reject) => {
        const curl = new Curl();
        curl.enable(CurlFeature.Raw);
        curl.setOpt('URL', uri);
        curl.setOpt('FOLLOWLOCATION', true);

        curl.on('end', function (statusCode, data, headers) {
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

exports.hook_data = function (next, connection) {
    connection.transaction.parse_body = true;
    next();
};

exports.extract_links_from_body = function (body) {
    const plugin = this;

    var result = new Array();
    const content_type = libmime.parseHeaderValue(body.header.get_decoded('content-type')).value;

    switch (content_type) {
        case 'text/html':
            const extracted_from_html = plugin.extract_links_from_html(body.bodytext);
            result.push(...extracted_from_html);
            break;
        case 'multipart/alternative':
        case 'multipart/mixed':
            if (body.children) {
                for (var i = 0; i < body.children.length; i++) {
                    const extracted_from_body = plugin.extract_links_from_body(body.children[i]);
                    result.push(...extracted_from_body);
                }
            }
            break;
    }

    return result;
};

exports.hook_data_post = function (next, connection) {
    const plugin = this;

    const txn = connection.transaction;

    var links = plugin.extract_links_from_body(txn.body);

    Promise.all(links.map(l => plugin.check_link(l))).then(() => {
        next();
    }).catch(err => {
        plugin.logerror(err);
        // TODO parse error & call next(DENYSOFT) if internal error
        next(DENY);
    });
};

exports.hook_lookup_rdns = function (next, connection) {
    next(OK);
};
