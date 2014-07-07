/* global console, define */
define(['sjcl', 'jquery', 'underscore'], function(sjcl, $, _) {

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
     * use standart image or hide allocated image spaces and comments
     * if noscript has no content
     * @param  {object} $wrapper image area containing noscript
     */
    var hideImages = function( $img_wrapper, alt_source ){
        if ( alt_source ){
            $img_wrapper.html( '<img src="' +alt_source+ '"/>' );
        }else{
            $img_wrapper.height( 'auto' );
            $( '.cp__comment__count__wrap' ).hide();
        }
    };

    /**
     * rescale one image
     * @param  {[type]} image
     * @param  {[type]} subsequent
     * @param  {[type]} width
     * @param  {[type]} height
     */
    var rescaleOne = function(image, subsequent, width, height) {
        var $img = $(image);
        width = width || $img.width();

        // workaround for width = 'auto'
        if (!width) {
            width = $img.width('100%').width();
            $img.width('');
        }

        if (subsequent && $img.closest('.is-pixelperfect').length) {
            // get the parent height, don’t use ratio to update pixelperfect img
            // it also possible to pass the height delivering element via data-wrap
            var selector = $img.parent().attr('data-wrap'),
                wrapper = selector ? $img.closest(selector) : [];

            if (wrapper.length) {
                height = wrapper.innerHeight();
            } else {
                height = $img.parent().parent().innerHeight();
            }

        } else {
            //ToDo (T.B.) $img.height() has a wrong value if alt attribute is set in image
            //height = height || $img.height() || Math.round(width / $img.data('ratio'));
            height = height || Math.round(width / $img.data('ratio'));
        }

        var token = prefix(Math.ceil(width), Math.ceil(height));
        var src = image.src || $img.data('src');
        image.src = src.replace(/\/bitblt-\d+x\d+-[a-z0-9]+/, token);
    };

    /**
     * rescale all images
     * @param  {[type]} e
     */
    var rescaleAll = function(e) {
        if (!e) {
            // initial case, no images there yet, so create them
            $('.scaled-image > noscript').each(function() {
                var $noscript = $(this);
                var $parent = $noscript.parent();
                var markup = $noscript.text();

                if ( markup.trim() !== '' ){

                    markup = markup.replace('src="', 'data-src="');
                    $parent.html(markup);
                    var $imgs = $parent.find('img');
                    var width = 0;
                    var height = 0;
                    $imgs.each(function() {
                        var $img = $(this);

                        // add event triggering to tell the world
                        $img.on('load', function(e) {
                            $img.trigger('scaling_ready');
                        });

                        if ($parent.hasClass('is-pixelperfect')) {
                            var selector = $img.parent().attr('data-wrap'),
                                wrapper = selector ? $img.closest(selector) : [];

                            // use explicit width and height from responsive image parent element or data-wrap element
                            if (wrapper.length) {
                                width  = wrapper.width();
                                height = wrapper.innerHeight();
                            } else {
                                width  = $parent.width();
                                height = $parent.innerHeight();
                            }

                            rescaleOne(this, false, width, height);
                        } else {
                            // determine size of image from width + ratio of original image
                            rescaleOne(this, false);
                        }

                        resp_imgs.push(this);
                    });

                }else{
                // noscript doesn't has any content we can read (which might happen in older browsers)
                // therefore we have to hide allocated image spaces
                    hideImages( $parent, $noscript.attr('data-src'));
                }

            });
        } else {
            // rescale after resize, images already set up, just update
            for (var i = 0; i < resp_imgs.length; i++) {
                rescaleOne(resp_imgs[i], true);
            }
        }
    };

    /**
     * init scaling
     */
    var init = function() {
        rescaleAll();
        var lazy_rescaleAll = _.debounce(rescaleAll, 1000);
        $(window).on('resize', lazy_rescaleAll);
    };

    return {
        init: init
    };

});
