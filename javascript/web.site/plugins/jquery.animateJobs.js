/**
 * @fileOverview jQuery plugin to animate jobbox
 * @author anika.szuppa@zeit.de
 * @version  0.1
 */

(function( $ ) {

    $.fn.animateJobs = function() {

        var box = {
            $jobs: false,
            maxJobs: 0,
            current: 0,
            getJobList: function( $box ) {
                return ( $box.find( '.jb-content' ) );
            }
        };

        function animateJobs() {

            console.debug( box.$jobs[box.current] );

            $( box.$jobs[box.current] ).hide();

            if ( box.current !== box.maxJobs ) {
                box.current++;
            } else {
                box.current = 0;
            }

            $( box.$jobs[box.current] ).show();

        }

        //run through search element and return object
        return this.each( function() {
            box.$jobs = box.getJobList( $( this ) );
            box.maxJobs = box.$jobs.length - 1;
            setInterval( animateJobs, 5000 );
        });
    };

})( jQuery );
