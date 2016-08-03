/**
 * @fileOverview Module Photocluster
 * @version  0.1
 */
/**
 * photocluster.js: module for photocluster
 * @module photocluster
 */
define([ 'jquery' ], function( $ ) {

    /**
     * photocluster.js: initialize photocluster
     * @function init
     */
    var init = function() {
        var $cluster = $('.photocluster');

        if ($cluster.length) {
            var $photos = $cluster.children();
            var classes = ['size-s', 'size-m', 'size-l'];
            var noGlobal = ( window.jQuery !== $ );

            // hack for old library freewall.js
            // make sure that jQuery is in the global scope
            if ( noGlobal ) {
                window.jQuery = window.$ = $;
            }

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
                // remove jQuery from global scope again
                if ( noGlobal ) {
                    $.noConflict( true );
                }

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
