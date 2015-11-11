/**
 * @fileOverview jQuery Plugin for Dropdown in Studiumbox
 * @author anika.szuppa@zeit.de
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
    * handles dropdown in studium box
    * @class boxDropdown
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.studiumDropdown = function() {

        var el = {
            bindDropboxEvents: function( $form ) {
                console.debug( $form );
                var $select = $form.find( '.studiumbox__input' );

                $select.on( 'change', function( event ) {
                    console.debug( this.val() );
                });

                // var f = this.form, o = this.options[this.selectedIndex];
                //     f.ab.value = o.getAttribute('data-ab');
                //     f.hstyp.value = o.getAttribute('data-hstyp');
                //     f.subfach.value = o.getAttribute('data-subfach');

            }
        };

        return this.each( function() {
            el.bindDropboxEvents( this );
        });
    };
})( jQuery );
