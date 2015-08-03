/**
 * @fileOverview jQuery Plugin for animated scrolling
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
(function( $ ) {

    var defaults = {
        duration: 500
    };

    /**
     * See (http://jquery.com/).
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
     * Animate scrolling for elements
     * @class animateScroll
     * @memberOf jQuery.fn
     * @param {object} options configuration object, overwriting presetted options
     * @return {object} jQuery-Object for chaining
     */
    $.fn.scrollIntoView = function( options ) {

        options = $.extend( {}, defaults, options );

        // this.eq( 0 ).velocity( 'scroll', { duration: options.duration } );
        $( 'html, body' ).stop().animate({
            scrollTop: this.eq( 0 ).offset().top
        }, options.duration );

        return this;
    };
})( jQuery );
