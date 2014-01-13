/* global console, define, alert, sjcl */

define(['jquery'], function() {

    var prefix = function(width, height) {
        var key = width + ':' + height + ':time';
        var out = sjcl.hash.sha1.hash(key);
        var digest = sjcl.codec.hex.fromBits(out);
        return '/bitblt-' + width + 'x' + height + '-' + digest;
    };

    var rescale = function(image) {
        var origin = location.origin;
        var url = origin + prefix(Math.round(image.width / 8), Math.round(image.height / 8));
        image.src = image.src.replace(origin, url);
    };

    var init = function() {
        $('img.figure__media').each(function() {
            rescale(this);
        });
    };

    return {
        init: init
    };

});
