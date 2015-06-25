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

        var toggle = $( '#beta-toggle' ),
            action = toggle.attr( 'action' ) + '/json',
            /**
             * showRequestWait – visualize status while waiting for request
             * completion
             * @param  {object} elem jQuery-Object of the input
             */
            showRequestWait = function( label ) {
                if ( !label.children().length ) {
                    label.siblings().find( '.beta-teaser__status' ).remove();
                    $( '<span class="beta-teaser__status icon-beta-throbber">' ).appendTo( label );
                }
            },
            /**
             * showRequestComplete – visualize status after request completion
             * @param  {object} elem jQuery-Object of the input
             */
            showRequestComplete = function( label ) {
                var span = label.children( 'span' ).first();
                span.removeClass( 'icon-beta-throbber' );
                span.addClass( 'icon-beta-toggle_done' );
            };
        $( '#opt-out', this ).click(function() {
            var elem = this,
                label = $( elem ).next( 'label' );
            showRequestWait( label );
            jQuery.post( action, { 'opt': 'out' }, function() {
                showRequestComplete( label );
            } ).fail( function() {
                $( '#opt-in' ).attr( 'checked', 'checked' );
            });
        });

        $( '#opt-in', this ).click(function() {
            var elem = this,
                label = $( elem ).next( 'label' );
            showRequestWait( label );
            jQuery.post( action, { 'opt': 'in' }, function() {
                showRequestComplete( label );
            } ).fail( function() {
                $( '#opt-out' ).attr( 'checked', 'checked' );
            });
        });

        return this;
    };

})( jQuery );
