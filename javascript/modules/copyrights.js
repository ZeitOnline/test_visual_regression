/* global console, define */
define(['jquery'], function() {

    /**
     * Toggle copyrights area
     */
    var toggleCopyrights = function(e) {
        var area = $('.copyrights');

        e.preventDefault();

        area.slideToggle('slow');
    };

    /**
     * Scroll to bottom of page
     */
    var scrollToBottom = function(e) {
        var target = $('html,body');

        e.preventDefault();

        target.animate({scrollTop: target.height()}, 1000);
    };

    /**
     * Initialize copyrights toggling
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
