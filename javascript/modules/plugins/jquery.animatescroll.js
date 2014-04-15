/* global console, alert */
(function($){

    'use strict';

    var defaults = {
        selector: null
    };

    /**
     * animate scrolling for anchor links
     */
    $.fn.animateScroll = function(options) {

        options = $.extend({}, defaults, options);

        /**
         * run through links that jump to anchors
         * return to chain jQuery functions
         */
        return this.each(function() {
            $(this).on('touchstart click', options.selector, function(e) {
                var anchor = this.hash.slice(1), // remove '#'
                    target;

                if (anchor) {
                    target = document.getElementById(anchor) || document.getElementsByName(anchor)[0];
                }

                if (!target) {
                    return;
                }

                e.preventDefault();

                $('html, body').stop().animate({
                    scrollTop: $(target).offset().top
                }, 500);
            });
        });

    };
})(jQuery);
