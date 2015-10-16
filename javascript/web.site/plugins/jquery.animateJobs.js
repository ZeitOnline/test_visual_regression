/**
 * @fileOverview jQuery plugin to animate jobbox
 * @author anika.szuppa@zeit.de
 * @version  0.1
 */

(function( $ ) {

    $.fn.animateJobs = function() {

        var box = {
            current: 0,
            maxJobs: 0,
            getJobList: function( $box ) {
                return ( $box.find( '.jb-content' ) );
            },
            toggleJob: function( $jobs ) {

                $( $jobs[box.current] ).velocity( 'fadeOut', { delay: 2000, display: 'none', duration: 2000 } );

                if ( box.current !== box.maxJobs ) {
                    box.current++;
                } else {
                    box.current = 0;
                }

                $( $jobs[box.current] ).velocity( 'fadeIn', { delay: 3500, display: 'inline-block', duration: 2000 } );

                box.toggleJob( $jobs );
            }
        };

        function animateJobs( $box ) {
            var $jobs = box.getJobList( $box );
            box.maxJobs = $jobs.length - 1;
            box.toggleJob( $jobs );
        }

        //run through search element and return object
        return this.each( function() {
            var that = $( this );
            animateJobs( that );
        });
    };

})( jQuery );
