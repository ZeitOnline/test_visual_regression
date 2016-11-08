(function( $, window ) {
    $.extend({
        notifications: function() {
            var location = window.location,
                msgRegistrationSuccess = '<div class="notification notification--success" tabindex="0">' +
                    'Herzlich willkommen! Mit Ihrer Anmeldung können Sie nun unsere Artikel lesen.</div>';

            // display hash only when loading article page from email-link
            if ( location.hash.substr( 1 ) === 'success-registration' ) {
                var $header = $( 'header' ).first();
                $( msgRegistrationSuccess ).insertAfter( $header );
                if ( 'replaceState' in history ) {
                    history.replaceState( null, document.title, location.pathname + location.search );
                } else {
                    location.hash = null;
                }
            } else {
                return false;
            }
        }
    });
})( jQuery, window );
