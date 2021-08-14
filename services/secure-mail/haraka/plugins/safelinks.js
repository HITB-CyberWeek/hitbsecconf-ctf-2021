// safelinks

const { Curl } = require('node-libcurl');
const NodeClam = require('clamscan');
const Readable = require('stream').Readable;

exports.register = function () {
    const plugin = this;

    plugin.load_config();
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

exports.check_links = function(next, connection) {
        var plugin = this;

        plugin.loginfo("Started check_links");

        const ClamScan = new NodeClam().init({
            debug_mode: true,
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

        const rs = Readable();
        rs.push('foooooo');
        rs.push('barrrrr');
        rs.push(null);

        ClamScan.then(clamscan => {
            clamscan.get_version((err, version) => {
                if (err) return plugin.logerror(err);
                plugin.loginfo(`ClamAV Version: ${version}`);
            });

            clamscan.scan_stream(rs, (err, result) => {
                if (err) return plugin.logerror(err);
                const {is_infected} = result;

                if (is_infected) return plugin.loginfo("Stream is infected! Booo!");
                plugin.loginfo("Stream is not infected! Yay!");
            });
        });

/*
        var curl = new Curl();
        curl.setOpt('URL', 'gopher://mongodb:27017/1%9e%00%00%00%03%00%00%00%00%00%00%00%dd%07%00%00%01%00%00%00%01%32%00%00%00%64%6f%63%75%6d%65%6e%74%73%00%24%00%00%00%07%5f%69%64%00%60%fd%39%7b%ec%32%11%2c%88%05%68%bd%02%6e%61%6d%65%00%04%00%00%00%66%6f%6f%00%00%00%52%00%00%00%02%69%6e%73%65%72%74%00%05%00%00%00%74%65%73%74%00%08%6f%72%64%65%72%65%64%00%01%03%6c%73%69%64%00%1e%00%00%00%05%69%64%00%10%00%00%00%04%4b%38%cf%30%6c%df%4a%f8%85%68%2d%db%4f%f1%86%7c%00%02%24%64%62%00%05%00%00%00%74%65%73%74%00%00%d1%6b%5c%9b')
        curl.setOpt('FOLLOWLOCATION', true);

        curl.on('end', function (statusCode, data, headers) {
            plugin.loginfo(statusCode);
            plugin.loginfo(data.length);
            plugin.loginfo(this.getInfo( 'TOTAL_TIME'));

            this.close();
        });

        curl.on('error', function (error, errorCode) {
            plugin.logerror(error.toString());
            curl.close.bind(curl);
        });

        curl.perform();
*/
        plugin.loginfo("Ended check_links");

	next();
};
