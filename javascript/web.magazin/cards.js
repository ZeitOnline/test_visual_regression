/**
 * @fileOverview Module for flipping cards
 * @version  0.1
 */
/**
 * cards.js: module for flipping cards
 * @module cards
 */
define([ 'jquery' ], function( $ ) {

    /**
     * cards.js: flip card
     * @function flipCard
     * @param {object} e event object
     */
    function flipCard( e ) {
        var deck = $( this ).closest( '.card__deck' );
        e.preventDefault();
        deck.toggleClass( 'js-flipped' );
    }

    /**
     * cards.js: slide card
     * @function slideCard
     * @param {object} e event object
     */
    function slideCard( e ) {
        var deck = $( this ).closest( '.card__deck' );
        e.preventDefault();
        deck.toggleClass( 'js-slid' );
    }

    /**
     * cards.js: stop propagation
     * @function stopPropagation
     * @param {object} e event object
     */
    function stopPropagation( e ) {
        e.stopImmediatePropagation();
    }

    /**
     * cards.js: initialize flipping cards
     * @function init
     */
    function init() {
        var node = $( 'main' );

        node.on( 'click', '.js-flip-card', flipCard )
            .on( 'click', '.js-slide-card', slideCard )
            .on( 'click', '.js-stop-propagation', stopPropagation );
    }

    return {
        init: init
    };

});
