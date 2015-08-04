/**
 * @fileOverview jQuery Plugin for copyrights
 * @author moritz.stoltenburg@zeit.de
 * @version  0.2
 */
(function( $ ) {

    var defaults = {
        duration: 500,
        selector: null
    };

    $.fn.copyrights = function( options ) {

        options = $.extend( {}, defaults, options );

        return this.each( function() {
            $( this ).on( 'click', options.selector, function( e ) {
                var $copyrights = $( '#copyrights' );

                e.preventDefault();

                if ( $copyrights.is( ':hidden' ) ) {
                    $copyrights.css({ display: 'block' }).scrollIntoView({ duration: options.duration });
                } else {
                    $copyrights.slideUp( options.duration );
                }
            });
        });

    };
})( jQuery );
