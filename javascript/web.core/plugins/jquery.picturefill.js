/**
 * @fileOverview jQuery Plugin to include picturefill polyfill
 * @author moritz.stoltenburg@zeit.de
 * @version 0.1
 */
define([ 'jquery' ], function( $ ) {

    $.extend({
        /**
         * Require picturefill asynchronous on request
         * @memberOf jQuery
         * @category Function
         */
        picturefill: function() {
            var container = $( '.x-picturefill' );

            if ( container.length ) {
                require([
                    'picturefill'
                ], function( picturefill ) {
                    picturefill({
                        elements: container.get()
                    });
                });
            }
        }
    });

    return {};

});
