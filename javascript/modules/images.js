/* global console, define, alert, sjcl, _ */
define(['sjcl', 'jquery', 'underscore'], function(sjcl) {

    var resp_imgs = [];

    /**
     * [prefix description]
     * @param  {[type]} width
     * @param  {[type]} height
     * @return {[type]}
     */
    var prefix = function(width, height) {
        var key = width + ':' + height + ':time';
        var out = sjcl.hash.sha1.hash(key);
        var digest = sjcl.codec.hex.fromBits(out);
        return '/bitblt-' + width + 'x' + height + '-' + digest;
    };

    /**
     * rescale one image
     * @param  {[type]} image
     * @param  {[type]} subsequent
     * @param  {[type]} width
     * @param  {[type]} height
     */
    var rescale_one = function(image, subsequent, width, height) {
        var $img = $(image);
        width = width || $img.width();
        if (subsequent && $img.parents('.is-pixelperfect').length) {
            // get the parent height, don’t use ratio to update pixelperfect img
            // it also possible to pass the height delivering element via data-wrap
            if( $img.parent().attr('data-wrap') ){
                height = $($img.parent().attr('data-wrap')).height();
            }else{
                height = $img.parent().parent().height();
            }

        } else {
            //ToDo (T.B.) $img.height() has a wrong value if alt attribute is set in image
            //height = height || $img.height() || Math.round(width / $img.data('ratio'));
            height = height || Math.round(width / $img.data('ratio'));
        }
        var token = prefix(width, height);
        var src = image.src || $img.data('src');
        image.src = src.replace(/\/bitblt-\d+x\d+-[a-z0-9]+/, token);
        // add event triggering to tell the world
        $(image).on("load", function(e){
            $(this).trigger("scaling_ready");
        });
    };

    /**
     * rescale all images
     * @param  {[type]} e
     */
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
                var height = 0;
                var width = 0;
                $imgs.each(function() {
                    if ($parent.hasClass('is-pixelperfect')) {

                        // use explicit width and height from responsive image parent element or data-wrap element
                        if( $(this).parent().attr('data-wrap') ){
                            height = $($(this).parent().attr('data-wrap')).height();
                            width = $($(this).parent().attr('data-wrap')).width();
                        }else{
                            height = $parent.parent().height();
                            width = $parent.parent().width();
                        }

                        rescale_one(this, false, width, height);
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

    /**
     * init scaling
     */
    var init = function() {
        rescale_all();
        var lazy_rescale_all = _.debounce(rescale_all, 1000);
        $(window).on('resize', lazy_rescale_all);
    };

    return {
        init: init
    };

});
