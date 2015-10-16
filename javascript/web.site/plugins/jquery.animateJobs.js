/**
 * @fileOverview jQuery plugin to animate jobbox
 * @author anika.szuppa@zeit.de
 * @version  0.1
 */

(function( $ ) {

    $.fn.animateJobs = function() {

        $.each( ['show', 'hide'], function( i, ev ) {
            var el = $.fn[ev];
            $.fn[ev] = function() {
                this.trigger( ev );
                return el.apply( this, arguments );
            };
        }) ;

        var box = {
            current: 0,
            maxJobs: 0,
            jobs: false,
            getJobList: function( $box ) {
                return ( $box.find( '.jb-content' ) );
            },
            setCurrentJob: function() {

                if ( box.current !== box.maxJobs ) {
                    box.current++;
                } else {
                    box.current = 0;
                }

            },
            hideJob: function( $jobs ) {

                $( box.jobs[box.current] ).find( '.jb-text' ).delay( 10000 ).velocity( 'fadeOut', 3000, function() {
                    $( box.jobs[box.current] ).removeClass( 'jb-content--show' );
                    box.setCurrentJob();
                    box.showJob();
                });

            },
            showJob: function() {
                $( box.jobs[box.current] ).addClass( 'jb-content--show' );
                $( box.jobs[box.current] ).find( '.jb-text' ).velocity( 'fadeIn', 3000, function() {
                    box.hideJob();
                });

            }
        };

        //run through search element and return object
        return this.each( function() {
            box.jobs = box.getJobList( $( this ) );
            box.maxJobs = box.jobs.length - 1;
            box.hideJob();
        });
    };

})( jQuery );
