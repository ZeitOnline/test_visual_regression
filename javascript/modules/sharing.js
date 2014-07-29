/* global console, define */

/**
 * @fileOverview Module for sharing functionality
 * @version  0.1
 */
/**
 * sharing.js: module for sharing
 * @module sharing
 */
define(['jquery'], function() {

    var $socialServices = $('#js-social-services');

    /**
     * sharing.js: toggle sharing box
     * @function toggleSharing
     */
    var toggleSharing = function() {
        $(this)
            .find('.article__sharing__icon')
            .toggleClass('icon-sharebox-share')
            .toggleClass('icon-sharebox-close');
        $socialServices.find('.article__sharing__services').toggleClass('blind');
    };

    /**
     * sharing.js: initialize sharing section
     * @function init
     */
    var init = function() {
        // register event handlers
        $socialServices.on('click', '.js-toggle-sharing', toggleSharing);
    };

    return {
        init: init
    };

});
