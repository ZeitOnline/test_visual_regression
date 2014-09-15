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
            });

            /**
             * require photocluster library
             */
            require( [
                'freewall'
            ], function( freewall ) {
                var wall = new freewall('.photocluster');
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

                $cluster.on( 'scaling_ready', function() {
                    wall.fitWidth();
                });
            });
        }
    };

    return {
        init: init
    };

});
