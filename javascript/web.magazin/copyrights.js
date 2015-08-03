/**
 * @fileOverview Module for copyrights
 * @version  0.1
 */
/**
 * copyrights.js: module for copyrights
 * @module copyrights
 */
define(['jquery'], function() {

    /**
     * copyrights.js: toggle copyrights
     * @function toggleCopyrights
     * @param  {object} e event object
     */
    var toggleCopyrights = function( e ) {
        var $copyrights = $( '#copyrights' ),
            duration = 500;

        e.preventDefault();

        if ( $copyrights.is( ':hidden' ) ) {
            $copyrights.css({ display: 'block' }).velocity( 'scroll', duration );
        } else {
            $copyrights.velocity( 'slideUp', duration );
        }

    };

    /**
     * copyrights.js: initialize copyrights toggling
     * @function init
     */
    var init = function() {
        $( '.page-wrap' ).on( 'click', '.js-toggle-copyrights', toggleCopyrights );
    };

    return {
        init: init
    };

});
