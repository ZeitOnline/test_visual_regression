/**
 * @fileOverview Displays login-state in nav dynamically, based on the cookie. Used on external sites (via framebuilder).
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
define([], function() {

    var cookieValue,
        navLoginArea,
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

        var userName = 'Konto';
        if ( userObject.name ) {
            userName = userObject.name;
            log( 'Label set to name: ' + userObject.name );
        } else if ( userObject.email ) {
            userName = userObject.email;
            log( 'Label set to email: ' + userObject.email );
        }

        // first step: very simple
        var loginLink = document.querySelector( '.nav__login-link' );
        if ( loginLink ) {
            loginLink.setAttribute( 'href', window.Zeit.actualHost + '/konto' );
            loginLink.innerText = userName;
        }

        // second step: complex layout update
        var template = require( 'web.core/templates/framebuilderLoginStatus.html' ),
            newDom = template({
                username: userName,
                returnurl: encodeURIComponent( window.location.href )
            });

        navLoginArea.innerHTML = newDom;
    }

    return {
        init: function() {
            cookieValue = window.Zeit.cookieRead( 'zeit_sso_201501' );
            log( 'cookieValue: ' + cookieValue );

            if ( cookieValue ) {
                navLoginArea = document.querySelector( '.nav__login' );
                // this is double-negative, so we can remove everything as soon
                // as we do not need the safety net any longer
                if ( navLoginArea && navLoginArea.getAttribute( 'data-featuretoggle' ) !== 'disable-loginstatus' ) {
                    updateNavLoginArea();
                }
            }
        }
    };
});
