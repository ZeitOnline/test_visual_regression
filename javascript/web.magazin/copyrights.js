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
    var toggleCopyrights = function(e) {
        var area = $('.copyrights');
        e.preventDefault();
        area.slideToggle('slow');
    };

    /**
     * copyrights.js: scroll to bottom of page
     * @function scrollToBottom
     * @param  {object} e event object
     */
    var scrollToBottom = function(e) {
        var target = $('html,body');
        e.preventDefault();
        target.animate({scrollTop: target.height()}, 1000);
    };

    /**
     * copyrights.js: initialize copyrights toggling
     * @function init
     */
    var init = function() {
        var node = $('.page-wrap');
        node.on('click', '.js-toggle-copyrights', toggleCopyrights);
        node.on('click', '.js-toggle-copyrights', scrollToBottom);
    };

    return {
        init: init
    };

});
