( function( $, location, document ) {
    $.extend({
        notifications: function() {
            var prepend = $( '.header' ).length > 0 ? false : true,
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
                },
                insertNotification = function( $message, prepend ) {
                    if ( prepend ) {
                    // we have to prepend if there is no header (eg. wrapper app)
                        $message.prependTo( $( '.page__content' ) );
                    } else {
                    // otherwise we insert after header element
                        $message.insertAfter( $( '.header' ) );
                    }
                    removeHash();
                };

            switch ( location.hash.substr( 1 ) ) {
                case 'success-registration':
                    if ( window.Zeit.view.hasOwnProperty( 'paywall' ) && window.Zeit.view.paywall === 'paid' ) {
                        insertNotification( $( msgRegistrationErrorWrongSubscription ), prepend );
                    } else {
                        insertNotification( $( msgRegistrationSuccess ), prepend );
                    }
                    break;
                case 'success-confirm-account':
                    insertNotification( $( msgAccountConfirmSuccess ), prepend );
                    break;
                case 'success-confirm-change':
                    insertNotification( $( msgChangeConfirmSuccess ), prepend );
                    break;
            }
        }
    });
})( jQuery, location, document );
