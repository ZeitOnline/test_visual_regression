/* global console, define */
define(['jquery'], function() {

   /**
     * Flip card
     */
    var flipCard = function(e) {
        var deck = $(this).closest('.card__deck');

        e.preventDefault();

        deck.toggleClass('js-flipped');
    };

   /**
     * Slide card
     */
    var slideCard = function(e) {
        var deck = $(this).closest('.card__deck');

        e.preventDefault();

        deck.toggleClass('js-slid');
    };

   /**
     * Initialize flipping cards
     */
    var init = function() {
        console.log('init');

        $('main').on('click', '.js-flip-card', flipCard);
        $('main').on('click', '.js-slide-card', slideCard);
    };

    return {
        init: init
    };

});
