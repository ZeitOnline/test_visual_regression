/**
 * @fileOverview jQuery Plugin for additional functionality in infoboxes
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
(function( $, win ) {
    /**
    * See (http://jquery.com/)
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
    * additional functionality for otherwise css powered infoboxes
    * @class infobox
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.infobox = function() {
        var pos,
            ltIE9 = ( $('html.lt-ie9').size() > 0 );
        return this.each( function() {
            // fallback for ie lower 9
            if (ltIE9) {
                $('.infobox__tab').eq(0).find('.infobox__inner').addClass('infobox__inner--active');
            }
            // marking actual tab (which on't work in CSS)
            $('.infobox__navlabel').on('click', function( evt ) {
                $('.infobox__navlabel.infobox__navlabel--checked').removeClass('infobox__navlabel--checked');
                $(evt.target).addClass('infobox__navlabel--checked');
                // fallback for ie lower 9
                if (ltIE9) {
                    pos = $(evt.target).parent().prevAll().size();
                    $('.infobox__tab .infobox__inner').removeClass('infobox__inner--active');
                    $('.infobox__tab').eq(pos).find('.infobox__inner').addClass('infobox__inner--active');
                }
            });
        });
    };
})( jQuery, window );
