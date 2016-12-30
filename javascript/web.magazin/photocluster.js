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
        var $cluster = $( '.js-photocluster' );

        // only load photocluster library if there is more than one column
        if ( $cluster.length && $cluster.css( 'position' ) === 'relative' ) {

            /**
             * require photocluster library
             */
            require( [
                'masonry'
            ], function( Masonry ) {

                new Masonry( '.js-photocluster', {
                    itemSelector: '.photocluster__media',
                    columnWidth: '.photocluster__media--small',
                    percentPosition: true
                });

            });
        }
    };

    return {
        init: init
    };

});
