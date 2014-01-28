/* global console, define, alert, sjcl, _ */

define(['jquery', 'underscore'], function() {

    var resp_imgs = [];

    var prefix = function(width, height) {
        var key = width + ':' + height + ':time';
        var out = sjcl.hash.sha1.hash(key);
        var digest = sjcl.codec.hex.fromBits(out);
        return '/bitblt-' + width + 'x' + height + '-' + digest;
    };

    var rescale_one = function(image, subsequent, width, height) {
        var $img = $(image);
        width = width || $img.width();
        if (subsequent && $img.parents('.is-pixelperfect').length) {
            // get the parent height, don’t use ratio to update pixelperfect img
            height = $img.parent().parent().height();
        } else {
            height = height || $img.height() || Math.round(width / $img.data('ratio'));
        }
        var token = prefix(width, height);
        var src = image.src || $img.data('src');
        image.src = src.replace(/\/bitblt-\d+x\d+-[a-z0-9]+/, token);
    };

    var rescale_all = function(e) {
        if (!e) {
            // initial case, no images there yet, so create them
            $('.scaled-image > noscript').each(function() {
                var $noscript = $(this);
                var $parent = $noscript.parent();
                var markup = $noscript.text();
                markup = markup.replace('src="', 'data-src="');
                $parent.html(markup);
                var $imgs = $parent.find('img');
                $imgs.each(function() {
                    if ($parent.hasClass('is-pixelperfect')) {
                        // use explicit width and height from responsive image parent element
                        rescale_one(this, false, $parent.parent().width(), $parent.parent().height());
                    } else {
                        // determine size of image from width + ratio of original image
                        rescale_one(this, false);
                    }
                    resp_imgs.push($imgs[0]);
                });
            });
        } else {
            // rescale after resize, images already set up, just update
            for(var i=0; i<resp_imgs.length; i++) {
                rescale_one(resp_imgs[i], true);
            }
        }
    };

    var init = function() {
        rescale_all();
        var lazy_rescale_all = _.debounce(rescale_all, 1000);
        $(window).on('resize', lazy_rescale_all);
    };

    return {
        init: init
    };

});
