(function( $, location, document ) {
    $.extend({
        notifications: function() {
            var $header = $( 'header' ).first(),
                msgRegistrationSuccess = '<div class="notification notification--success" tabindex="0">' +
                    'Herzlich willkommen – viel Spaß beim Lesen!</div>',
                msgRegistrationErrorWrongSubscription = '<div class="notification notification--error" tabindex="0">' +
                    'Leider haben Sie kein gültiges Abonnement für diesen Artikel. Bitte wählen Sie unten das gewünschte Abo.</div>',
                msgAccountConfirmSuccess = '<div class="notification notification--success" tabindex="0">' +
                    'Herzlich willkommen! Ihr Konto ist nun aktiviert.</div>',
                msgChangeConfirmSuccess = '<div class="notification notification--success" tabindex="0">' +
                    'Ihre Einstellungen wurden gespeichert. Viel Spaß!</div>',
                removeHash = function() {
                    if ( 'replaceState' in history ) {
                        history.replaceState( null, document.title, location.pathname + location.search );
                    } else {
                        location.hash = null;
                    }
                };

            // display hash only when loading page from email-link

            switch ( location.hash.substr( 1 ) ) {
                case 'success-registration':
                    if ( window.Zeit.view.hasOwnProperty( 'paywall' ) && window.Zeit.view.paywall === 'paid' ) {
                        $( msgRegistrationErrorWrongSubscription ).insertAfter( $header );
                    } else {
                        $( msgRegistrationSuccess ).insertAfter( $header );
                    }
                    removeHash();
                    break;
                case 'success-confirm-account':
                    $( msgAccountConfirmSuccess ).insertAfter( $header );
                    removeHash();
                    break;
                case 'success-confirm-change':
                    $( msgChangeConfirmSuccess ).insertAfter( $header );
                    removeHash();
                    break;
            }

        }
    });
})( jQuery, location, document );
