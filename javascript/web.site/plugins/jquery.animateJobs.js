/**
 * @fileOverview jQuery plugin to animate jobbox
 * @author anika.szuppa@zeit.de
 * @version  0.1
 */
(function( $ ) {

    function Jobbox( element ) {
        var box = $( element );

        this.current = 0;
        this.jobs = box.find( '.jobbox__job' );
        this.button = box.find( '.jobbox__button' );

        if ( this.jobs.length ) {
            this.showJob();
        }
    }

    Jobbox.prototype.showNext = function() {
        this.current = ( this.current + 1 ) % this.jobs.length;
        this.showJob();
    };

    Jobbox.prototype.showJob = function() {
        var box = this,
            job = this.jobs.eq( this.current ),
            link = job.attr( 'href' );

        this.button.attr( 'href', link );
        job
            .velocity( 'transition.slideUpIn', { duration: 500, display: 'block' } )
            .velocity( 'transition.slideUpOut', {
                duration: 500,
                delay: 8000,
                complete: function() {
                    box.showNext();
                }
            });
    };

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
        return this.each( function() {
            new Jobbox( this );
        });
    };

})( jQuery );
