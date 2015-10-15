/**
 * @fileOverview jQuery plugin to animate jobbox
 * @author anika.szuppa@zeit.de
 * @version  0.1
 */

(function( $ ) {

    $.fn.animateJobs = function() {

        var box = {
            animateJobs: function( $jobs ) {
                window.console.debug( 'yes2' );
            }
        };

        //run through search element and return object
        return this.each( function() {

            var jobs = $( this ).find( '.jb-content' );
            setInterval( box.animateJobs( jobs ), 100 );

        });
    };

})( jQuery );
