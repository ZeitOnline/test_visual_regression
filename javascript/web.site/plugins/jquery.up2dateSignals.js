/* global console */

/**
 * @fileOverview jQuery Plugin for animating text chunks
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
(function( $ ) {
    /**
    * See (http://jquery.com/)
    * @name jQuery
    * @alias $
    * @class jQuery Library
    * See the jQuery Library  (http://jquery.com/) for full details.  This just
    * documents the function and classes that are added to jQuery by this plug-in.
    */
    /**
    * See (http://jquery.com/)
    * @name fn
    * @class jQuery Library
    * See the jQuery Library  (http://jquery.com/) for full details.  This just
    * documents the function and classes that are added to jQuery by this plug-in.
    * @memberOf jQuery
    */
    /**
    * Animates any given text chunk from dom value to new value
    * @class animateText
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.animateText = function( options ) {
        // extend default values with delivered options
        var defaults = $.extend({
            inEffect: { opacity: 0 },
            inVelocity: 500,
            outEffect: { opacity: 1 },
            outVelocity: 500
        }, options),
        textanimation = function( elem, text ) {
            text = text || elem.text();
            var textarr = text.split( ' ' ),
            elems = elem.blast({
                delimiter: 'word',
                aria: true,
                generateValueClass: true
            });

            //
            // elemsToAnimate = [];

            // elems.each( function( i, n ) {
            //     if ( $(n).text() !== textarr[i] ) {
            //         elemsToAnimate.push( i );
            //     }
            // });

            // elems.each( function( i, n ) {
            //     if ( $.inArray(i, elemsToAnimate) > -1 ) {
            //         $(n).animate( defaults.inEffect, defaults.inVelocity, function() {
            //             $(this)
            //             .html( textarr[i] )
            //             .delay( 10 )
            //             .animate( defaults.outEffect, defaults.outVelocity);
            //         });
            //     }
            // });
        };
        //run through search element and return object
        return this.each( function() {
            // var counter = 1,
            // $that = $(this),
            // interval = window.setInterval(function() {
            //     counter++;
            //     textanimation( $that, 'vor ' + counter + ' Minuten' );
            // }, 10000);

        });
    };
})( jQuery );
