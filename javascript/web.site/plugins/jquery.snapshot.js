/* global GWPLine, GWPLine3, nsIqd_setBg */
/**
* ZON Snapshot formally know as Bottompic Plugin
* snapshot picture is loaded after the part of the page is in the visible area
*
* Copyright (c) 2011-14 ZEIT ONLINE, http://www.zeit.de
* Dual licensed under the MIT and GPL licenses:
* http://www.opensource.org/licenses/mit-license.php
* http://www.gnu.org/licenses/gpl.html
*
* @author Nico Bruenjes
* @version 2.0
*
*/
(function($) {

    $.fn.snapshot = function( options ) {
        var defaults = $.extend({
                triggerElement: '.main__parquet'
            }, options),
            that = this;
        return this.each( function() {
            $( defaults.triggerElement ).on( 'inview', function( evt ) {
                $( that ).addClass('snapshot--blurred');
                $( that ).show(0, function() {
                    // change html5 prop "hidden" (which is more accessible)
                    $( this ).prop('hidden', false);
                    // resize triggers image load
                    $(window).resize();
                    // jscs:disable
                    // callback fuer GWPBanner, Erwin Senk, 18.07.2011
                    if (typeof window.GWPLine !== 'undefined' && typeof window.GWPLine3 !== 'undefined') {
                        window.GWPLine.init();
                        window.GWPLine3.init2();
                    }
                    if (typeof window.nsIqd_setBg !== 'undefined') {
                        window.nsIqd_setBg();
                    }
                    // jscs:enable
                    $( that ).removeClass('snapshot--blurred');
                });
                $( this ).unbind( 'inview' );
            });
        });
    };

})( jQuery );
