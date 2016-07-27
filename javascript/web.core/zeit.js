// jscs:disable requireCamelCaseOrUpperCaseIdentifiers
/**
 * @fileOverview ZEIT ONLINE core javascript module [Zeit]
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
define( function() {
    var Zeit = window.Zeit || {},
        extension = {
            clickCount: {
                webtrekk: function( id ) {
                    // webtrekk
                    if ( id !== undefined && 'wt' in window && typeof window.wt.sendinfo === 'function' ) {
                        window.wt.sendinfo({
                            linkId: id + window.location.pathname
                        });
                    }
                },
                ga: function( id ) {
                    // google analytics
                    if ( typeof window._gaq !== 'undefined' ) {
                        window._gaq.push([ '_trackEvent', id + window.location.pathname, 'click' ]);
                    }
                },
                ivw: function() {
                    // IVW
                    if ( 'iom' in window && typeof window.iom.h === 'function' && typeof window.iam_data !== 'undefined' ) {
                        window.iom.h( window.iam_data, 1 );
                    }
                },
                cc: function() {
                    // cc tracking
                    var img = document.createElement( 'img' );
                    img.src = 'http://cc.zeit.de/cc.gif?banner-channel=' + encodeURIComponent( Zeit.view.banner_channel ) +
                                '&amp;r=' + encodeURIComponent( document.referrer ) +
                                '&amp;rand=' + Math.random() * 100000;
                },
                all: function( id ) {
                    // start all tracking functions
                    if ( id ) {
                        this.webtrekk( id );
                        this.ga( id );
                    }
                    this.cc();
                    this.ivw();
                }
            },
            clearQueue: function() {
                // fix for external jQuery Plugins (e.g. Datenjornalismus)
                // remove as soon as we find something better
                if ( this.queue.length ) {
                    require([ 'jquery' ], function( $ ) {
                        window.jQuery = window.$ = $;
                    });
                }

                for ( var i = 0, l = this.queue.length; i < l; i++ ) {
                    require.apply( window, this.queue[i] );
                }

                this.queue = [];
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
