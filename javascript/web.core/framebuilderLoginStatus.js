/**
 * @fileOverview Displays login-state in nav dynamically, based on the cookie. Used on external sites (via framebuilder).
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
define([], function() {

    var cookieValue,
        userObject,
        debug = window.location.hash.indexOf( 'debug-framebuilderlogin' ) !== -1;

    function log() {
        if ( debug ) {
            console.log.apply( console, arguments );
        }
    }

    function parseJwt( token ) {
        var base64Url = token.split( '.' )[ 1 ];
        var base64 = base64Url.replace( '-', '+' ).replace( '_', '/' );
        return JSON.parse( window.atob( base64 ) );
    }

    function updateNavLoginArea() {
        userObject = parseJwt( cookieValue );
        log( 'userObject: ', userObject );

        var loginLink = document.querySelector( '.nav__login-link' );
        if ( loginLink ) {
            loginLink.setAttribute( 'href', window.Zeit.actualHost + '/konto' );
            if ( userObject.name ) {
                loginLink.innerText = userObject.name;
                log( 'Label set to name: ' + userObject.name );
            } else if ( userObject.email ) {
                loginLink.innerText = userObject.email;
                log( 'Label set to email: ' + userObject.email );
            } else {
                loginLink.innerText = 'Konto';
                log( 'Label set to default: Konto' );
            }
        }
    }

    return {
        init: function() {
            cookieValue = window.Zeit.cookieRead( 'zeit_sso_201501' );
            log( 'cookieValue: ' + cookieValue );

            if ( cookieValue ) {
                updateNavLoginArea();
            }
        }
    };
});
