/* global console, define, alert, sjcl */

define(['jquery'], function() {

    var rescale_threshold = 1.5;

    var prefix = function(width, height) {
        var key = width + ':' + height + ':time';
        var out = sjcl.hash.sha1.hash(key);
        var digest = sjcl.codec.hex.fromBits(out);
        return '/bitblt-' + width + 'x' + height + '-' + digest;
    };

    var rescale = function(image) {
        if (image.width / image.naturalWidth < rescale_threshold) {
            return;     // rescaling is not needed...
        }
        var origin = location.origin;
        var token = prefix(image.width, image.height);
        image.src = image.src.replace(/\/bitblt-\d+x\d+-[a-z0-9]+/, token);
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
