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
define([ 'jquery' ], function( $ ) {

    /**
     * articlesharing.js: toggle sharing menu
     * @function toggleSharing
     */
    var toggleSharing = function( event ) {
        event.preventDefault();
        $( this ).parent().toggleClass( 'sharing-menu--active' );
    },

    /**
     * articlesharing.js: initialize sharing menu
     * @function init
     */
    init = function() {
        // register event handler
        $( '.js-sharing-menu' ).on( 'click', toggleSharing );
    };

    return {
        init: init
    };

});
