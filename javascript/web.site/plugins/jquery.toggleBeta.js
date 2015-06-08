/**
* @fileOverview Zeit Online Plugin to toggle beta state
* @version  0.1
*
* Plugin progressivley enhances form to set beta state
*
* Copyright (c) 2014 ZEIT ONLINE, http://www.zeit.de
* Dual licensed under the MIT and GPL licenses:
* http://www.opensource.org/licenses/mit-license.php
* http://www.gnu.org/licenses/gpl.html
*
* @author Ron Drongowski
*/

(function( $ ) {
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
     * Click submit, when beta state is set
     * @class toggleBeta
     * @memberOf jQuery.fn
    */

    $.fn.toggleBeta = function() {

        var toggle = $( '#beta-toggle' );

        $( '#opt-out', this ).click(function() {
            jQuery.post( toggle.attr( 'action' ), { 'opt': 'out' } ).fail( function() {
                $( '#opt-in' ).attr( 'checked', 'checked' );
            });
        });

        $( '#opt-in', this ).click(function() {
            jQuery.post( toggle.attr( 'action' ), { 'opt': 'in' } ).fail( function() {
                $( '#opt-out' ).attr( 'checked', 'checked' );
            });
        });

        return this;
    };

})( jQuery );
