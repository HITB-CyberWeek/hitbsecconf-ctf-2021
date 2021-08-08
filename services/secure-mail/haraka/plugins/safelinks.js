// safelinks

const { Curl } = require('node-libcurl');

exports.register = function () {
    this.register_hook('data', 'check_links');
};

exports.check_links = function(next, connection) {
        var plugin = this;

        plugin.loginfo("Started check_links");

        var curl = new Curl();
//        curl.setOpt('URL', 'gopher://192.168.88.201:7070/_%31%00%32%00');
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

        plugin.loginfo("Ended check_links");

	next();
};
