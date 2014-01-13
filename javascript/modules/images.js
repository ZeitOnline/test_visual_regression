/* global console, define, alert, sjcl */

define(['jquery'], function() {

    var prefix = function(width, height) {
        var key = width + ':' + height + ':time';
        var out = sjcl.hash.sha1.hash(key);
        var digest = sjcl.codec.hex.fromBits(out);
        return '/bitblt-' + width + 'x' + height + '-' + digest;
    };

    var scale = function(image, width, height) {
        var origin = location.origin;
        image.src = image.src.replace(origin, origin + prefix(width, height));
    };

    var init = function() {
        $('img.figure__media').each(function() {
            scale(this, 80, 60);
        });
    };

    return {
        init: init
    };

});
