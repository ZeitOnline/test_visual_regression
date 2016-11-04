(function( $, window ) {
    $.fn.notifications = function() {
        var location = window.location,
            msg_registration_success = "<div class='notification notification--success notification--registration'>" +
                "<span class='notification notification__message'>Herzlich willkommen! Mit Ihrer Anmeldung können Sie nun unsere Artikel lesen.</span></div>";
        if ( location.hash.substr( 1 ) === 'registration_success' ) {
            $( msg_registration_success ).insertAfter( 'header' );
            if ("replaceState" in history) {
                history.replaceState( "", document.title, location.pathname + location.search );
            } else {
                location.hash = "";
            }
        } else {
            return;
        }
    };
})( jQuery, window);
