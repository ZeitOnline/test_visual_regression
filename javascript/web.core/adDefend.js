/**
 * @fileOverview Module adDefend
 * @author jan-paul.bauer@zeit.de
 * @version  0.1
 */

function AdDefend() {
    // general config
    this.config = {
        template: require( 'web.core/templates/addefend.html' ), // the template we use
        windowHeight: window.Zeit.view.get( 'addefend_height' ), // config zeitweb-settings, mobileView is always 500px
        jsonPath: '/json/addefend/addefend.json', // config zeitweb-settings for path to config file
        inViewElement: '.footer', // hide notice bar when footer is in view
        cookieName: 'addefend', // cookiename for AdDefend
        cookieExpire: window.Zeit.view.get( 'addefend_cookie_expire' ), // config zeitweb-settings for expiringtime for cookies
        trackingId: '#adb' // identifier for clicktracking
    };

    this.path = '//' + window.location.host + this.config.jsonPath;
    this.init();
}

AdDefend.prototype.getData = function( url ) {
    return new window.Promise( function( resolve, reject ) {
        var xhr = new XMLHttpRequest(),
            errorURL;
        xhr.open( 'GET', url );
        xhr.onload = function() {
            // this is called even on 404 etc
            // so check the status
            if ( xhr.status === 200 ) {
                // resolve the promise with the settings text
                resolve( JSON.parse( xhr.response ) );
            } else {
                // otherwise reject with the status text
                // error out meaningfully w/ request URL if possible
                errorURL = xhr.responseURL ? ': ' + xhr.responseURL : '';
                reject( Error( xhr.statusText + errorURL ) );
            }
        };
        // handle network errors
        xhr.onerror = function() {
            reject( Error( 'Network Error' ) );
        };
        // make the request
        xhr.send();
    });
};

AdDefend.prototype.renderTemplate = function() {

    // text for different sections from json-file
    var html = this.config.template({
        hl: this.responseObj.headline_notice,
        description: this.responseObj.description,
        btnDeactivate: this.responseObj.btn_deactivate,
        notice: this.responseObj.notice,
        hlManual: this.responseObj.hl_manual,
        listManual1: this.responseObj.list_manual1,
        listManual2: this.responseObj.list_manual2,
        listManual3: this.responseObj.list_manual3,
        btnReload: this.responseObj.btn_reload
    });

    document.querySelector( 'body' ).insertAdjacentHTML( 'beforeend', html );
};

AdDefend.prototype.handleOverlay = function() {
    var that = this;
    var addefendwrapper = document.querySelector( '#addefend-overlay' );
    var addefenddark = document.querySelector( '.page' );

    // tracking
    that.track( 'view', 'banner', that.config.trackingId );

    // darken page 50% opacity
    addefenddark.classList.add( 'addefend__darken' );

    require([
        'jquery',
        'web.core/zeit',
        'jquery.inview'
    ],
    function( $, Zeit ) {
        // hide if footer is in view
        $( that.config.inViewElement ).on( 'inview', function( event, isInView ) {
            if ( isInView ) {
                addefendwrapper.classList.add( 'addefend--hidden' );
                addefenddark.classList.remove( 'addefend__darken' );
            } else {
                addefendwrapper.classList.remove( 'addefend--hidden' );
                addefenddark.classList.add( 'addefend__darken' );
            }
        });

        // dismiss-Button
        $( '#addefend-dismiss' ).click( function() {
            $( '#addefend-note' ).fadeOut();

            // tracking
            that.track( 'view', 'banner', that.config.trackingId );

            var overlayHeight;

            if ( that.config.windowHeight === 'max' ) {
                overlayHeight = $( window ).height();
            } else if ( that.config.windowHeight === 'min' ) {
                overlayHeight = '600';
            } else if ( Zeit.isMobileView() ) {
                overlayHeight = '500';
            }

            $( '#addefend-overlay' ).delay( 300 ).animate({
                height: overlayHeight
            }, 400 );

            // fadein manual
            $( '#addefend-manual' ).delay( 500 ).fadeIn();

            // keep update-overlay back
            Zeit.cookieCreate( 'overlaycanceled', 'canceled', that.config.cookieExpire );

            // track click
            that.track( 'deactivate', 'banner', that.config.trackingId );
        });

        // reload-button
        $( '#addefend-reload' ).click( function() {
            location.reload();

            // tracking
            that.track( 'refresh', 'anleitung', that.config.trackingId );
        });

        // remove layer and add cookie
        $( '.addefend__notification' ).click( function() {
            $( '#addefend-overlay' ).fadeOut( 200, function() {
                $( this ).remove();
            });

            // track click
            that.track( 'cancel', '', that.config.trackingId );

            // hide addefend notice for the time that are set in the config
            var date = new Date();
            var minutes = that.config.cookieExpire;
            date.setTime( date.getTime() + ( minutes * 60 * 1000 ) );

            document.cookie = that.config.cookieName + '=' + 'true' + ';path=/;expires=' + date.toGMTString();

            // light up page
            document.querySelector( '.page' ).classList.remove( 'addefend__darken' );
        });
    });
};

AdDefend.prototype.track = function( action, section, identifier ) {
    require([ 'web.core/clicktracking' ], function( Clicktracking ) {
        var data = [ 'sitebottom.' + section + '...' + action, identifier ];
        Clicktracking.send( data );
    });
};

AdDefend.prototype.init = function() {
    var that = this;
    // only init when cookie is not set
    if ( document.cookie.indexOf( that.config.cookieName ) <= 0  ) {
        that.getData( that.path ).then( function( response ) {
            that.responseObj = response;
        }).then( function() {
            that.renderTemplate();
            that.handleOverlay();
            that.track();
        });
    }
};

new AdDefend();

module.exports = AdDefend;
