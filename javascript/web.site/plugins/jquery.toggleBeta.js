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

(function( $, win, doc ) {
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
     * @param {string} arg methodname to call from plugin, if ommited, init is called
     * @param {*} [options…] arguments to methods
    */

    $.fn.toggleBeta = function( arg ) {

        var that = this;

        $( '#opt-out', this ).click(function() {
            that.submit();
        });

        $( '#opt-in', this ).click(function() {
            that.submit();
        });

        $( '#beta-toggle-submit', this ).hide();

        return this;
    };

})( jQuery, window, document );
