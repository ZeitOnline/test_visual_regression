/**
 * @fileOverview Module adDefend
 * @author jan-paul.bauer@zeit.de
 * @version  0.1
 */

var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    clicktracking = require( 'web.core/clicktracking' );

function AdDefend() {
    // general config
    this.config = {
        template: require( 'web.core/templates/addefend.html' ), // the template we use
        windowHeight: zeit.view.get( 'addefend_height' ), // config zeitweb-settings, mobileView is always 500px
        jsonPath: '/json/addefend/addefend.json', // config zeitweb-settings for path to config file
        inViewElement: '.footer', // hide notice bar when footer is in view
        cookieName: 'addefend', // cookiename for AdDefend
        cookieExpire: zeit.view.get( 'addefend_cookie_expire' ), // config zeitweb-settings for expiringtime for cookies
        trackingId: '#adb' // identifier for clicktracking
    };

    this.path = '//' + location.host + this.config.jsonPath;
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

AdDefend.prototype.renderTemplate = function( data ) {

    // text for different sections from json-file
    var html = this.config.template({
        hl: data.headline_notice,
        description: data.description,
        btnDeactivate: data.btn_deactivate,
        notice: data.notice,
        hlManual: data.hl_manual,
        listManual1: data.list_manual1,
        listManual2: data.list_manual2,
        listManual3: data.list_manual3,
        btnReload: data.btn_reload
    });

    document.querySelector( 'body' ).insertAdjacentHTML( 'beforeend', html );
};

AdDefend.prototype.handleOverlay = function() {
    var that = this;

    // view Overlay
    $( '#overlay-wrapper, #overlay-wrapper .overlay' ).fadeIn();

    // tracking
    this.track( 'view', 'banner', this.config.trackingId );

    // Show manual button
    $( '#addefend-guide' ).click( function() {
        $( '#addefend-note' ).fadeOut();

        // tracking
        that.track( 'view', 'banner', that.config.trackingId );

        var overlayHeight;

        if ( that.config.windowHeight === 'max' ) {
            overlayHeight = $( window ).height();
        } else if ( that.config.windowHeight === 'min' ) {
            overlayHeight = '600';
        } else if ( zeit.isMobileView() ) {
            overlayHeight = '500';
        }

        $( '#addefend-overlay' ).delay( 300 ).animate({
            height: overlayHeight
        }, 400 );

        // fadein manual
        $( '#addefend-manual' ).delay( 500 ).fadeIn();

        // keep update-overlay back
        zeit.cookieCreate( 'overlaycanceled', 'canceled', that.config.cookieExpire );

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
    $( '.addefend__dismiss' ).click( function() {
        $( '#addefend-overlay, #overlay-wrapper' ).fadeOut( 200, function() {
            $( this ).remove();
        });

        // track click
        that.track( 'cancel', '', that.config.trackingId );

        // hide addefend notice for the time that are set in the config
        zeit.cookieCreate( that.config.cookieName, 'true', that.config.cookieExpire );
    });
};

AdDefend.prototype.track = function( action, section, identifier ) {
    var data = [ 'sitebottom.' + section + '...' + action, identifier ];
    clicktracking.send( data );
};

AdDefend.prototype.init = function() {
    var that = this;
    // only init when cookie is not set
    if ( document.cookie.indexOf( this.config.cookieName ) <= 0  ) {
        this.getData( this.path ).then( function( response ) {
            that.renderTemplate( response );
            that.handleOverlay();
            that.track();
        });
    }
};

module.exports = AdDefend;
