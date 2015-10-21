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
            /**
             * getJobList – returns current list of job html objects
             * @param  {object} jobs jQuery-Object of the jobbox
             * @return {object}
             */
            getJobList: function( jobs ) {
                return ( $( jobs ).find( '.jb-content' ) );
            },
            /**
             * setCurrentJob – defines current job object in list
             * @param  {object} jobs jQuery-Object of the jobbox
             * @param  {integer} index of currently shown job
             * @return {integer}
             */
            setCurrentJob: function( jobs, current ) {
                return ( ( current + 1 ) % jobs.length );
            },
            /**
             * hideJob – fades out a job per animation
             * @param  {object} jobs jQuery-Object of the jobbox
             * @param  {integer} index of currently shown job
             */
            hideJob: function( jobs, current ) {
                $( jobs[current] ).find( '.jb-text' ).delay( 8000 ).velocity( 'transition.slideUpOut', 500, function() {
                    $( jobs[current] ).removeClass( 'jb-content--show' );
                    box.showJob( jobs, box.setCurrentJob( jobs, current ) );
                });
            },
            /**
             * showJob – fades in a job per animation
             * @param  {object} jobs jQuery-Object of the jobbox
             * @param  {integer} index of currently shown job
             */
            showJob: function( jobs, current ) {
                var link = $( jobs[current] ).attr( 'href' );
                $( jobs ).closest( 'aside' ).find( '.jb-button__link' ).attr( 'href', link );
                $( jobs[current] ).addClass( 'jb-content--show' );
                $( jobs[current] ).find( '.jb-text' ).velocity( 'transition.slideUpIn', 500, function() {
                    box.hideJob( jobs, current );
                });

            }
        };

        return this.each( function() {
            // as the first job is displayed by default,
            // we start with hiding it
            var jobs = box.getJobList( this );
            box.hideJob( jobs, 0 );
        });
    };

})( jQuery );
