/**
 * @fileOverview jQuery Plugin for counting characters in form fields
 * @author thomas.puppe@zeit.de
 * @version  0.1
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
    * Counts characters in form fields and displays the number on the page
    * @class countFormchars
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.countFormchars = function() {
        return this.each( function() {
            var $counter = $( this ),
                $formField = $( $counter.data( 'charcount-element' ) );

            $formField.on( 'change keyup paste', function( e ) {
                var formFieldContentLength = this.value.length;
                $counter.text( formFieldContentLength + ' / ' );
            } );
        });
    };
})( jQuery );
