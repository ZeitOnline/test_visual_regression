/* global console, alert */
(function($){

    /**
     * animate scrolling for anchor links
     */
    $.fn.animateScroll = function() {

        /**
         * run through links that jump to anchors
         */
        $(this).each(function() {
            $(this).click(function(e) {
                var anchor = $(this).attr('href').slice(1), // remove '#'
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
