/* global console */

/**
 * @fileOverview jQuery Plugin for animated scrolling
 * @version  0.1
 */
(function($){

    'use strict';

    var defaults = {
        selector: null
    };

    /**
     * See (http://jquery.com/).
     * @name jQuery
     * @alias $
     * @class jQuery Library
     * See the jQuery Library  (http://jquery.com/) for full details.  This just
     * documents the function and classes that are added to jQuery by this plug-in.
     */
    /**
     * See (http://jquery.com/)
     * @name fn
     * @class jQuery Library
     * See the jQuery Library  (http://jquery.com/) for full details.  This just
     * documents the function and classes that are added to jQuery by this plug-in.
     * @memberOf jQuery
     */
    /**
     * Animate scrolling for anchor links
     * @class animateScroll
     * @memberOf jQuery.fn
     * @param {object} options configuration object, overwriting presetted options
     * @return {object} jQuery-Object for chaining
     */
    $.fn.animateScroll = function(options) {

        options = $.extend({}, defaults, options);

        //run through links that jump to anchors
        return this.each(function() {
            $(this).on('click', options.selector, function(e) {
                var anchor = this.hash.slice(1), // remove '#'
                    target,
                    attribute;

                if (anchor) {
                    target = document.getElementById(anchor) || document.getElementsByName(anchor)[0];
                }

                if (!target) {
                    return;
                }

                e.preventDefault();

                // change location hash without page jump
                attribute = (target.id === anchor) ? 'id' : 'name';
                target[attribute] = '';
                location.hash = this.hash;
                target[attribute] = anchor;

                // animate scrolling
                $('html, body').stop().animate({
                    scrollTop: $(target).offset().top
                }, 500);
            });
        });

    };
})(jQuery);
