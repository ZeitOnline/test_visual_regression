/**
 * @fileOverview ZEIT ONLINE core javascript module [Zeit]
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
define( function() {
    var Zeit = window.Zeit || {},
        extension = {
            clearQueue: function() {
                for ( var i = 0, l = this.queue.length; i < l; i++ ) {
                    require.apply( window, this.queue[i] );
                }
            },
            cookieCreate: function( name, value, days, domain ) {
                var expires = '';

                if ( arguments.length < 4 ) {
                    domain = 'zeit.de';
                }

                if ( days ) {
                    var date = new Date();
                    date.setTime( date.getTime() + ( days * 24 * 60 * 60 * 1000 ) );
                    expires = '; expires=' + date.toGMTString();
                }

                document.cookie = name + '=' + value + expires + '; path=/; domain=' + domain;
            },
            cookieRead: function( name ) {
                return ( document.cookie.match( '(?:^|;) ?' + name + '\\s*=\\s*([^;]*)' ) || 0 )[1];
            }
        },
        key;

    for ( key in extension ) {
        if ( extension.hasOwnProperty( key ) ) {
            Zeit[ key ] = extension[ key ];
        }
    }

    return Zeit;
});
