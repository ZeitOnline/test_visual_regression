/**
 * @fileOverview jQuery Plugin for calling the Sharebert feature on
 * article blocks.
 * @author thomas.puppe@zeit.de
 * @version 0.1
 */
( function( $ ) {

    'use strict';

    var debugMode = location.hash.indexOf( 'debug-shareblocks' ) > -1;

    function log() {
        if ( debugMode ) {
            var args = Array.prototype.slice.call( arguments );
            console.log.apply( console, args );
        }
    }

    function ShareBlock( rootElement ) {
        this.rootElement = rootElement;
        this.clickEventListener = null;
        this.init();
    }

    var getSharebertData = function( sharebertShotUrl, sharebertRedirectUrl ) {
        return new window.Promise( function( resolve, reject ) {

            var metaData = {
                'title': document.title,
                'description': document.querySelector( 'meta[name=description]' ).getAttribute( 'content' )
            };
            var myData = {
                'target_url': sharebertShotUrl,
                'meta_data': metaData,
                'redirect_to': sharebertRedirectUrl
            };

            var xhr = new XMLHttpRequest();
            xhr.open( 'POST', 'http://share.zeit.de/-/apps/twitter-quote/shots' );
            xhr.onload = function() {
                // This is called even on 404 etc
                // so check the status
                if ( xhr.status === 200 ) {
                    // Resolve the promise with the response text
                    resolve( JSON.parse( xhr.response ) );
                } else {
                    // Otherwise reject with the status text
                    // which will hopefully be a meaningful error
                    reject( Error( xhr.statusText ) );
                }
            };
            // Handle network errors
            xhr.onerror = function() {
                reject( Error( 'Network Error' ) );
            };
            // Make the request
            xhr.setRequestHeader( 'Content-Type', 'application/json; charset=utf-8' );
            xhr.send( JSON.stringify( myData ) );

        });
    };

    var clickEventListener = function() {

        var linkElement = this.rootElement.querySelector( '.quote-sharing__link--twitter' ),
            sharebertRedirectUrl = linkElement.getAttribute( 'data-sharebert-redirect-url' ),
            sharebertShotUrl = linkElement.getAttribute( 'data-sharebert-screenshot-target' );

        // for testing locally (Sharebert cannot reach your localhost), use ngrok or:
        // sharebertShotUrl = 'http://live0.zeit.de/twitter-quote/?quote=Das%20hat%20alles%20keinen%20Gin.';

        log( 'sharebertRedirectUrl: ' + sharebertRedirectUrl );
        log( 'sharebertShotUrl: ' + sharebertShotUrl );

        getSharebertData( sharebertShotUrl, sharebertRedirectUrl )
            .then( function( response ) {
                log( 'SUCCESS, got URL:' + response.src_url );
                var shareLink = 'https://twitter.com/intent/tweet?text=' + encodeURIComponent( response.src_url );
                linkElement.setAttribute( 'href', shareLink );
            }, function( error ) {
                log( 'ERROR', error );
            });

        $( this.itemsElement ).velocity( 'transition.slideRightIn', {
            display: 'inline-block', // remove the property altogether and return to previous display value from CSS
            duration: 300
        });

        this.labelElement.removeEventListener( 'click', this.clickEventListener );
        this.labelElement.classList.remove( 'js-shareblock__label' ); // this makes cursor:pointer

        this.track( 'open', sharebertShotUrl );
    };

    ShareBlock.prototype.track = function( action, url ) {
        log( 'Track: ' + action + ': ' + url );
        require([ 'web.core/clicktracking' ], function( Clicktracking ) {
            var data = [ 'shareblock....' + action, url.replace( /http(s)?:\/\//, '' ) ];
            Clicktracking.send( data );
        });
    };

    ShareBlock.prototype.init = function() {
        this.labelElement = this.rootElement.querySelector( '.js-shareblock__label' );
        this.itemsElement = this.rootElement.querySelector( '.js-shareblock__items' );

        this.itemsElement.style.display = 'none';

        // bind this on runtime to make it revokable
        this.clickEventListener = clickEventListener.bind( this );
        this.labelElement.addEventListener( 'click', this.clickEventListener );
    };

    $.fn.shareBlocks = function() {

        // Promises working since iOS Safari8, Android Browser 4.4.4, Chrome+FF+Opera+Edge.
        // Promise not working in IE 11.
        // Fallback is the regular share URL
        // That way, we can also use XMLHttpRequest with a JSON response.
        if ( !window.Promise ) {
            return;
        }

        return this.each( function() {
            new ShareBlock( this );
        });
    };
})( jQuery );
