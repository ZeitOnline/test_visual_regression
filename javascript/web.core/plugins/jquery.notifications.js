(function( $, window ) {
    $.fn.notifications = function() {
        var location = window.location,
            msgRegistrationSuccess = '<div class="notification notification--success">' +
                '<span>Herzlich willkommen! Mit Ihrer Anmeldung können Sie nun unsere Artikel lesen.</span></div>';
        if ( location.hash.substr( 1 ) === 'registration_success' ) {
            $( msgRegistrationSuccess ).insertAfter( 'header' );
            if ( 'replaceState' in history ) {
                history.replaceState( null, document.title, location.pathname + location.search );
            } else {
                location.hash = null;
            }
        } else {
            return;
        }
    };
})( jQuery, window );
