(function( $, location, document ) {
    $.extend({
        notifications: function() {
            var msgRegistrationSuccess = '<div class="notification notification--success" tabindex="0">' +
                    'Herzlich willkommen! Mit Ihrer Anmeldung können Sie nun unsere Artikel lesen.</div>',
                msgRegistrationErrorWrongSubscription = '<div class="notification notification--error" tabindex="0">' +
                    'Leider haben Sie kein gültiges Abonnement für diesen Artikel. Bitte wählen Sie unten das gewünschte Abo.</div>';

            // display hash only when loading article page from email-link
            if ( location.hash.substr( 1 ) === 'success-registration' ) {
                var $header = $( 'header' ).first();

                if ( window.Zeit.view.hasOwnProperty( 'paywall' ) && window.Zeit.view.paywall === 'paid' ) {
                    $( msgRegistrationErrorWrongSubscription ).insertAfter( $header );
                } else {
                    $( msgRegistrationSuccess ).insertAfter( $header );
                }

                if ( 'replaceState' in history ) {
                    history.replaceState( null, document.title, location.pathname + location.search );
                } else {
                    location.hash = null;
                }
            }
        }
    });
})( jQuery, location, document );
