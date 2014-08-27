/* global console, define */

/**
 * @fileOverview Module Photocluster
 * @version  0.1
 */
/**
 * photocluster.js: module for photocluster
 * @module photocluster
 */
define(['require', 'jquery'], function(require, $) {

    /**
     * photocluster.js: initialize photocluster
     * @function init
     */
    var init = function() {
        var $cluster = $('.photocluster');

        if ($cluster.length) {
            var $photos = $cluster.children();
            var classes = ['size-s', 'size-m', 'size-l'];

            // run through all photo boxes
            $photos.each(function(idx, photo){
                var $photo = $(photo);
                // add random sizing class
                $photo.addClass(classes[Math.floor(Math.random()*classes.length)]);
                // find responsive image container within packery block
                var $rimg = $photo.find('img, noscript').eq(0);
                if ($rimg.length === 1) {
                    // adjust height of packery block to ratio of image
                    // TODO: debounced recalculation on resize (see images.js for example)
                    $photo.css('height', $photo.width()/$rimg.data('ratio'));
                }
            });

            /**
             * photocluster.js: use Packery as a jQuery plugin with RequireJS, you’ll need to run jQuery bridget.
             * @tutorial http://packery.metafizzy.co/appendix.html#requirejs
             */
            require( [
                'libs/freewall'
            ], function( freewall ) {

                var wall = new freewall(".photocluster");
                wall.reset({
                    selector: '.photocluster__item',
                    animate: true,
                    cellW: 200,
                    cellH: 'auto',
                    onResize: function() {
                        wall.fitWidth();
                    }
                });
                wall.fitWidth();
            });
        }
    };

    return {
        init: init
    };

});
