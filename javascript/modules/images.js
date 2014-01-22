/* global console, define, alert, sjcl */

define(['jquery'], function() {

    var prefix = function(width, height) {
        var key = width + ':' + height + ':time';
        var out = sjcl.hash.sha1.hash(key);
        var digest = sjcl.codec.hex.fromBits(out);
        return '/bitblt-' + width + 'x' + height + '-' + digest;
    };

    var rescale = function(image, width, height) {
        var $img = $(image);
        width = width || $img.width();
        height = height || $img.height() || Math.round(width / $img.data('ratio'));
        var token = prefix(width, height);
        var src = image.src || $img.data('src');
        image.src = src.replace(/\/bitblt-\d+x\d+-[a-z0-9]+/, token);
    };

    var init = function() {
        $('.scaled-image > noscript').each(function() {
            var $noscript = $(this);
            var $parent = $noscript.parent();
            var markup = $noscript.text();
            markup = markup.replace('src="', 'data-src="');
            $parent.html(markup);
            $parent.find('img').each(function() {
                if ($parent.hasClass('is-pixelperfect')) {
                    // use explicit width and height from responsive image parent element
                    rescale(this, $parent.parent().width(), $parent.parent().height());
                } else {
                    // determine size of image from width + ratio of original image
                    rescale(this);
                }
            });
        });
    };

    return {
        init: init
    };

});
