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
        var $cluster = $('.js-photocluster');

        if ($cluster.length) {
            var $photos = $cluster.children();
            var noGlobal = ( window.jQuery !== $ );

            // hack for old library freewall.js
            // make sure that jQuery is in the global scope
            if ( noGlobal ) {
                window.jQuery = window.$ = $;
            }

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

                var wall = new freewall('.js-photocluster');
                wall.reset({
                    selector: '.photocluster__media',
                    animate: true,
                    cellW: 221,
                    cellH: 'auto',
                    gutterX: 12,
                    gutterY: 12,
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
