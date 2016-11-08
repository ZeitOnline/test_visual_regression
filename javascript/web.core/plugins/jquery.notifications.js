(function( $, window ) {
    $.fn.notifications = function() {
        var location = window.location,
            msgRegistrationSuccess = '<div class="notification notification--success" tabindex="0">' +
                '<span>Herzlich willkommen! Mit Ihrer Anmeldung können Sie nun unsere Artikel lesen.</span></div>';

        // display hash only when loading article page from email-link
        if ( location.hash.substr( 1 ) === 'registration_success' ) {
            var $header = $( 'header' ).first();
            $( msgRegistrationSuccess ).insertAfter( $header );
            if ( 'replaceState' in history ) {
                history.replaceState( null, document.title, location.pathname + location.search );
            } else {
                return false;
            }
        }
    });
})( jQuery, window );
