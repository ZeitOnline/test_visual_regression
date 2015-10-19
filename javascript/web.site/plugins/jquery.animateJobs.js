/**
 * @fileOverview jQuery plugin to animate jobbox
 * @author anika.szuppa@zeit.de
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
    * Animates Display of Jobs in Jobbox
    * @class animateJobs
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.animateJobs = function() {

        var box = {
            current: 0,
            maxJobs: 0,
            jobs: false,
            /**
             * getJobList – returns current list of job html objects
             * @param  {object} $box jQuery-Object of the jobbox
             * @return {object}
             */
            getJobList: function( $box ) {
                return ( $box.find( '.jb-content' ) );
            },
            /**
             * setCurrentJob – defines current job object in list
             */
            setCurrentJob: function() {
                if ( box.current !== box.maxJobs ) {
                    box.current++;
                } else {
                    box.current = 0;
                }
            },
            /**
             * hideJob – fades out a job per animation
             */
            hideJob: function() {

                $( box.jobs[box.current] ).find( '.jb-text' ).delay( 10000 ).velocity( 'fadeOut', 3000, function() {
                    $( box.jobs[box.current] ).removeClass( 'jb-content--show' );
                    box.setCurrentJob();
                    box.showJob();
                });

            },
            /**
             * showJob – fades in a job per animation
             */
            showJob: function() {
                $( box.jobs[box.current] ).addClass( 'jb-content--show' );
                $( box.jobs[box.current] ).find( '.jb-text' ).velocity( 'fadeIn', 3000, function() {
                    box.hideJob();
                });

            }
        };

        return this.each( function() {
            box.jobs = box.getJobList( $( this ) );
            box.maxJobs = box.jobs.length - 1;
            // as the first job is displayed by default,
            // we start with hiding it
            box.hideJob();
        });
    };

})( jQuery );
