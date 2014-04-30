/* global console, define */
define(['jquery'], function() {

   /**
     * Flip card
     */
    var flipCard = function(e) {
        var card = $(this).closest('.card');

        e.preventDefault();

        card.toggleClass('js-flipped');
    };

   /**
     * Slide card
     */
    var slideCard = function(e) {
        var card = $(this).closest('.card');

        e.preventDefault();

        card.toggleClass('js-slid');
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
