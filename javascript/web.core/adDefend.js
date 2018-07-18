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
        inViewElement: '.footer', // hide notice bar when footer is in view
        cookieName: 'addefend', // cookiename for AdDefend
        cookieExpire: zeit.view.get( 'addefend_cookie_expire' ), // config zeitweb-settings for expiringtime for cookies
        trackingId: '#adb' // identifier for clicktracking
    };

    // instantiate just once
    if ( !document.querySelector( '#addefend-overlay' ) ) {
        this.init();
    }
}

AdDefend.prototype.renderTemplate = function() {

    // text for different sections from json-file
    var html = this.config.template({
        hl: 'Bitte deaktivieren Sie Ihren Adblocker.',
        description: 'Durch die Ausspielung von Werbung unterstützen Sie die Refinanzierung unserer Berichterstattung. Vielen Dank!',
        btnDeactivate: 'Für zeit.de deaktivieren',
        notice: 'Mit AdBlocker weitersurfen',
        hlManual: 'So deaktivieren Sie den Ad Blocker',
        listManual1: 'Klicken Sie auf das Symbol des AdBlockers in Ihren Browser, um seine Einstellungen zu öffnen.',
        listManual2: 'Wählen Sie aus, dass Sie den AdBlocker für Seiten www.zeit.de deaktivieren wollen.',
        listManual3: 'Wenn Sie www.zeit.de auf die Whitelist gesetzt haben, laden Sie die Seite bitte neu.',
        btnReload: 'Seite aktualisieren'
    });

    document.querySelector( 'body' ).insertAdjacentHTML( 'beforeend', html );
};

AdDefend.prototype.handleOverlay = function() {
    var that = this;

    // view Overlay
    $( '#overlay-wrapper, #overlay-addefend' ).fadeIn();

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
        } else {
            overlayHeight = '500';
        }

        $( '#addefend-overlay' ).animate({ 'min-height': overlayHeight }, 400 );

        // fadein manual
        $( '#addefend-manual' ).delay( 500 ).fadeIn();

        // keep update-overlay back
        zeit.cookieCreate( 'overlaycanceled', 'canceled', that.config.cookieExpire );

        // track click
        that.track( 'deactivate', 'banner', that.config.trackingId );
    });

    // reload-button
    $( '#addefend-reload' ).click( function() {
        // tracking
        that.track( 'refresh', 'anleitung', that.config.trackingId );

        location.reload();
    });

    // remove layer and add cookie
    $( '.addefend__dismiss' ).click( function() {
        $( '#addefend-overlay, #overlay-addefend' ).fadeOut( 200, function() {
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
        that.renderTemplate();
        that.handleOverlay();
        that.track();
    }
};

module.exports = AdDefend;
