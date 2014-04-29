/* global console, define */
define(['jquery'], function() {

    var $socialServices = $('#js-social-services');

    /**
     * Toggle sharing box
     */
    var toggleSharing = function() {
        $(this).find('.article__sharing__icon').toggleClass('icon-sharebox-share').toggleClass('icon-sharebox-close');
        $socialServices.find('.article__sharing__services').toggleClass('blind');
    };

    /**
     * Initialize sharing section
     */
    var init = function() {
        // register event handlers
        $socialServices.on('click', '.js-toggle-sharing', toggleSharing);
    };

    return {
        init: init
    };

});
