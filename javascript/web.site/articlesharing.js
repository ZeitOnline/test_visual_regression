/**
 * @fileOverview sharing menu in articles
 * @author arne.seemann@zeit.de
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
/**
 * articlesharing.js: article sharing menu
 * @module articlesharing
 */
define([ 'jquery' ], function() {

    /**
     * articlesharing.js: toggle sharing menu
     * @function toggleSharing
     */
    var toggleSharing = function( clickEvent ) {
        $( clickEvent ).parent().toggleClass( 'sharing-menu--active' );
    },

    /**
     * articlesharing.js: initialize sharing menu
     * @function init
     */
    init = function() {
        // register event handler and pass event to the toggle function
        // thus it works properly if there's more than one sharing menu
        $( '.js-sharing-menu' ).on( 'click', function( event ) {
            toggleSharing( event.target );
        });
    };

    return {
        init: init
    };

});
