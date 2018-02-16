// jshint ignore: start
/*! modernizr 3.5.0 (Custom Build) | MIT *
 * https://modernizr.com/download/?-csstransforms-csstransforms3d-cssvhunit-cssvwunit-flexbox-preserve3d-svg-touchevents-video-printshiv-setclasses !*/
!( function( e, t, n ) {
    function r( e, t ) {
        return typeof e === t;
    } function o() {
        var e, t, n, o, i, a, s; for ( var l in S ) {
            if ( S.hasOwnProperty( l ) ) {
                if ( e = [], t = S[ l ], t.name && ( e.push( t.name.toLowerCase() ), t.options && t.options.aliases && t.options.aliases.length ) ) {
                    for ( n = 0; n < t.options.aliases.length; n++ ) {
                        e.push( t.options.aliases[ n ].toLowerCase() );
                    }
                } for ( o = r( t.fn, 'function' ) ? t.fn() : t.fn, i = 0; i < e.length; i++ ) {
                    a = e[ i ], s = a.split( '.' ), 1 === s.length ? Modernizr[ s[ 0 ] ] = o : ( !Modernizr[ s[ 0 ] ] || Modernizr[ s[ 0 ] ] instanceof Boolean || ( Modernizr[ s[ 0 ] ] = new Boolean( Modernizr[ s[ 0 ] ]) ), Modernizr[ s[ 0 ] ][ s[ 1 ] ] = o ), b.push( ( o ? '' : 'no-' ) + s.join( '-' ) );
                }
            }
        }
    } function i( e ) {
        var t = w.className, n = Modernizr._config.classPrefix || ''; if ( x && ( t = t.baseVal ), Modernizr._config.enableJSClass ) {
            var r = new RegExp( '(^|\\s)' + n + 'no-js(\\s|$)' ); t = t.replace( r, '$1' + n + 'js$2' );
        }Modernizr._config.enableClasses && ( t += ' ' + n + e.join( ' ' + n ), x ? w.className.baseVal = t : w.className = t );
    } function a() {
        return 'function' != typeof t.createElement ? t.createElement( arguments[ 0 ]) : x ? t.createElementNS.call( t, 'http://www.w3.org/2000/svg', arguments[ 0 ]) : t.createElement.apply( t, arguments );
    } function s() {
        var e = t.body; return e || ( e = a( x ? 'svg' : 'body' ), e.fake = !0 ), e;
    } function l( e, n, r, o ) {
        var i, l, c, u, d = 'modernizr', f = a( 'div' ), p = s(); if ( parseInt( r, 10 ) ) {
            for ( ;r--; ) {
            c = a( 'div' ), c.id = o ? o[ r ] : d + ( r + 1 ), f.appendChild( c );
        }
        } return i = a( 'style' ), i.type = 'text/css', i.id = 's' + d, ( p.fake ? p : f ).appendChild( i ), p.appendChild( f ), i.styleSheet ? i.styleSheet.cssText = e : i.appendChild( t.createTextNode( e ) ), f.id = d, p.fake && ( p.style.background = '', p.style.overflow = 'hidden', u = w.style.overflow, w.style.overflow = 'hidden', w.appendChild( p ) ), l = n( f, e ), p.fake ? ( p.parentNode.removeChild( p ), w.style.overflow = u, w.offsetHeight ) : f.parentNode.removeChild( f ), !!l;
    } function c( e, t ) {
        return !!~( '' + e ).indexOf( t );
    } function u( e ) {
    return e.replace( /([A-Z])/g, function( e, t ) {
        return '-' + t.toLowerCase();
    }).replace( /^ms-/, '-ms-' );
} function d( t, n, r ) {
    var o; if ( 'getComputedStyle' in e ) {
        o = getComputedStyle.call( e, t, n ); var i = e.console; if ( null !== o ) {
            r && ( o = o.getPropertyValue( r ) );
        } else if ( i ) {
            var a = i.error ? 'error' : 'log'; i[ a ].call( i, 'getComputedStyle returning null, its possible modernizr test results are inaccurate' );
        }
    } else {
        o = !n && t.currentStyle && t.currentStyle[ r ];
    } return o;
} function f( t, r ) {
    var o = t.length; if ( 'CSS' in e && 'supports' in e.CSS ) {
        for ( ;o--; ) {
            if ( e.CSS.supports( u( t[ o ]), r ) ) {
                return !0;
            }
        } return !1;
    } if ( 'CSSSupportsRule' in e ) {
        for ( var i = []; o--; ) {
            i.push( '(' + u( t[ o ]) + ':' + r + ')' );
        } return i = i.join( ' or ' ), l( '@supports (' + i + ') { #modernizr { position: absolute; } }', function( e ) {
            return 'absolute' == d( e, null, 'position' );
        });
    } return n;
} function p( e ) {
    return e.replace( /([a-z])-([a-z])/g, function( e, t, n ) {
        return t + n.toUpperCase();
    }).replace( /^-/, '' );
} function m( e, t, o, i ) {
    function s() {
        u && ( delete j.style, delete j.modElem );
    } if ( i = r( i, 'undefined' ) ? !1 : i, !r( o, 'undefined' ) ) {
        var l = f( e, o ); if ( !r( l, 'undefined' ) ) {
            return l;
        }
    } for ( var u, d, m, h, v, g = [ 'modernizr', 'tspan', 'samp' ]; !j.style && g.length; ) {
        u = !0, j.modElem = a( g.shift() ), j.style = j.modElem.style;
    } for ( m = e.length, d = 0; m > d; d++ ) {
        if ( h = e[ d ], v = j.style[ h ], c( h, '-' ) && ( h = p( h ) ), j.style[ h ] !== n ) {
            if ( i || r( o, 'undefined' ) ) {
                return s(), 'pfx' == t ? h : !0;
            } try {
                j.style[ h ] = o;
            } catch ( y ) {} if ( j.style[ h ] != v ) {
            return s(), 'pfx' == t ? h : !0;
        }
        }
    } return s(), !1;
} function h( e, t ) {
    return function() {
        return e.apply( t, arguments );
    };
} function v( e, t, n ) {
    var o; for ( var i in e ) {
        if ( e[ i ] in t ) {
            return n === !1 ? e[ i ] : ( o = t[ e[ i ] ], r( o, 'function' ) ? h( o, n || t ) : o );
        }
    } return !1;
} function g( e, t, n, o, i ) {
    var a = e.charAt( 0 ).toUpperCase() + e.slice( 1 ), s = ( e + ' ' + _.join( a + ' ' ) + a ).split( ' ' ); return r( t, 'string' ) || r( t, 'undefined' ) ? m( s, t, o, i ) : ( s = ( e + ' ' + z.join( a + ' ' ) + a ).split( ' ' ), v( s, t, n ) );
} function y( e, t, r ) {
    return g( e, n, n, t, r );
} var S = [], E = { _version: '3.5.0', _config: { classPrefix: '', enableClasses: !0, enableJSClass: !0, usePrefixes: !0 }, _q: [], on: function( e, t ) {
        var n = this; setTimeout( function() {
            t( n[ e ]);
        }, 0 );
    }, addTest: function( e, t, n ) {
        S.push({ name: e, fn: t, options: n });
    }, addAsyncTest: function( e ) {
        S.push({ name: null, fn: e });
    } }, Modernizr = function() {}; Modernizr.prototype = E, Modernizr = new Modernizr; var b = [], w = t.documentElement, x = 'svg' === w.nodeName.toLowerCase(); x || !( function( e, t ) {
        function n( e, t ) {
            var n = e.createElement( 'p' ), r = e.getElementsByTagName( 'head' )[ 0 ] || e.documentElement; return n.innerHTML = 'x<style>' + t + '</style>', r.insertBefore( n.lastChild, r.firstChild );
        } function r() {
            var e = C.elements; return 'string' == typeof e ? e.split( ' ' ) : e;
        } function o( e, t ) {
            var n = C.elements; 'string' != typeof n && ( n = n.join( ' ' ) ), 'string' != typeof e && ( e = e.join( ' ' ) ), C.elements = n + ' ' + e, c( t );
        } function i( e ) {
        var t = x[ e[ b ] ]; return t || ( t = {}, w++, e[ b ] = w, x[ w ] = t ), t;
    } function a( e, n, r ) {
        if ( n || ( n = t ), v ) {
            return n.createElement( e );
        } r || ( r = i( n ) ); var o; return o = r.cache[ e ] ? r.cache[ e ].cloneNode() : E.test( e ) ? ( r.cache[ e ] = r.createElem( e ) ).cloneNode() : r.createElem( e ), !o.canHaveChildren || S.test( e ) || o.tagUrn ? o : r.frag.appendChild( o );
    } function s( e, n ) {
        if ( e || ( e = t ), v ) {
        return e.createDocumentFragment();
    } n = n || i( e ); for ( var o = n.frag.cloneNode(), a = 0, s = r(), l = s.length; l > a; a++ ) {
        o.createElement( s[ a ]);
    } return o;
    } function l( e, t ) {
    t.cache || ( t.cache = {}, t.createElem = e.createElement, t.createFrag = e.createDocumentFragment, t.frag = t.createFrag() ), e.createElement = function( n ) {
        return C.shivMethods ? a( n, e, t ) : t.createElem( n );
    }, e.createDocumentFragment = Function( 'h,f', 'return function(){var n=f.cloneNode(),c=n.createElement;h.shivMethods&&(' + r().join().replace( /[\w\-:]+/g, function( e ) {
        return t.createElem( e ), t.frag.createElement( e ), 'c("' + e + '")';
    }) + ');return n}' )( C, t.frag );
} function c( e ) {
    e || ( e = t ); var r = i( e ); return !C.shivCSS || h || r.hasCSS || ( r.hasCSS = !!n( e, 'article,aside,dialog,figcaption,figure,footer,header,hgroup,main,nav,section{display:block}mark{background:#FF0;color:#000}template{display:none}' ) ), v || l( e, r ), e;
} function u( e ) {
    for ( var t, n = e.getElementsByTagName( '*' ), o = n.length, i = RegExp( '^(?:' + r().join( '|' ) + ')$', 'i' ), a = []; o--; ) {
        t = n[ o ], i.test( t.nodeName ) && a.push( t.applyElement( d( t ) ) );
    } return a;
} function d( e ) {
    for ( var t, n = e.attributes, r = n.length, o = e.ownerDocument.createElement( N + ':' + e.nodeName ); r--; ) {
        t = n[ r ], t.specified && o.setAttribute( t.nodeName, t.nodeValue );
    } return o.style.cssText = e.style.cssText, o;
} function f( e ) {
    for ( var t, n = e.split( '{' ), o = n.length, i = RegExp( '(^|[\\s,>+~])(' + r().join( '|' ) + ')(?=[[\\s,>+~#.:]|$)', 'gi' ), a = '$1' + N + '\\:$2'; o--; ) {
        t = n[ o ] = n[ o ].split( '}' ), t[ t.length - 1 ] = t[ t.length - 1 ].replace( i, a ), n[ o ] = t.join( '}' );
    } return n.join( '{' );
} function p( e ) {
    for ( var t = e.length; t--; ) {
        e[ t ].removeNode();
    }
} function m( e ) {
    function t() {
        clearTimeout( a._removeSheetTimer ), r && r.removeNode( !0 ), r = null;
    } var r, o, a = i( e ), s = e.namespaces, l = e.parentWindow; return !_ || e.printShived ? e : ( 'undefined' == typeof s[ N ] && s.add( N ), l.attachEvent( 'onbeforeprint', function() {
        t(); for ( var i, a, s, l = e.styleSheets, c = [], d = l.length, p = Array( d ); d--; ) {
            p[ d ] = l[ d ];
        } for ( ;s = p.pop(); ) {
            if ( !s.disabled && T.test( s.media ) ) {
                try {
                    i = s.imports, a = i.length;
                } catch ( m ) {
                    a = 0;
                } for ( d = 0; a > d; d++ ) {
                p.push( i[ d ]);
            } try {
                c.push( s.cssText );
            } catch ( m ) {}
            }
        }c = f( c.reverse().join( '' ) ), o = u( e ), r = n( e, c );
    }), l.attachEvent( 'onafterprint', function() {
        p( o ), clearTimeout( a._removeSheetTimer ), a._removeSheetTimer = setTimeout( t, 500 );
    }), e.printShived = !0, e );
} var h, v, g = '3.7.3', y = e.html5 || {}, S = /^<|^(?:button|map|select|textarea|object|iframe|option|optgroup)$/i, E = /^(?:a|b|code|div|fieldset|h1|h2|h3|h4|h5|h6|i|label|li|ol|p|q|span|strong|style|table|tbody|td|th|tr|ul)$/i, b = '_html5shiv', w = 0, x = {}; !( function() {
    try {
        var e = t.createElement( 'a' ); e.innerHTML = '<xyz></xyz>', h = 'hidden' in e, v = 1 == e.childNodes.length || ( function() {
            t.createElement( 'a' ); var e = t.createDocumentFragment(); return 'undefined' == typeof e.cloneNode || 'undefined' == typeof e.createDocumentFragment || 'undefined' == typeof e.createElement;
        })();
    } catch ( n ) {
        h = !0, v = !0;
    }
})(); var C = { elements: y.elements || 'abbr article aside audio bdi canvas data datalist details dialog figcaption figure footer header hgroup main mark meter nav output picture progress section summary template time video', version: g, shivCSS: y.shivCSS !== !1, supportsUnknownElements: v, shivMethods: y.shivMethods !== !1, type: 'default', shivDocument: c, createElement: a, createDocumentFragment: s, addElements: o }; e.html5 = C, c( t ); var T = /^$|\b(?:all|print)\b/, N = 'html5shiv', _ = !v && ( function() {
        var n = t.documentElement; return !( 'undefined' == typeof t.namespaces || 'undefined' == typeof t.parentWindow || 'undefined' == typeof n.applyElement || 'undefined' == typeof n.removeNode || 'undefined' == typeof e.attachEvent );
    })(); C.type += ' print', C.shivPrint = m, m( t ), 'object' == typeof module && module.exports && ( module.exports = C );
    })( 'undefined' != typeof e ? e : this, t ); var C = E._config.usePrefixes ? ' -webkit- -moz- -o- -ms- '.split( ' ' ) : [ '', '' ]; E._prefixes = C; var T = E.testStyles = l; Modernizr.addTest( 'touchevents', function() {
        var n; if ( 'ontouchstart' in e || e.DocumentTouch && t instanceof DocumentTouch ) {
            n = !0;
        } else {
            var r = [ '@media (', C.join( 'touch-enabled),(' ), 'heartz', ')', '{#modernizr{top:9px;position:absolute}}' ].join( '' ); T( r, function( e ) {
                n = 9 === e.offsetTop;
            });
        } return n;
    }), Modernizr.addTest( 'video', function() {
        var e = a( 'video' ), t = !1; try {
            t = !!e.canPlayType, t && ( t = new Boolean( t ), t.ogg = e.canPlayType( 'video/ogg; codecs="theora"' ).replace( /^no$/, '' ), t.h264 = e.canPlayType( 'video/mp4; codecs="avc1.42E01E"' ).replace( /^no$/, '' ), t.webm = e.canPlayType( 'video/webm; codecs="vp8, vorbis"' ).replace( /^no$/, '' ), t.vp9 = e.canPlayType( 'video/webm; codecs="vp9"' ).replace( /^no$/, '' ), t.hls = e.canPlayType( 'application/x-mpegURL; codecs="avc1.42E01E"' ).replace( /^no$/, '' ) );
        } catch ( n ) {} return t;
    }), Modernizr.addTest( 'svg', !!t.createElementNS && !!t.createElementNS( 'http://www.w3.org/2000/svg', 'svg' ).createSVGRect ); var N = 'Moz O ms Webkit', _ = E._config.usePrefixes ? N.split( ' ' ) : []; E._cssomPrefixes = _; var P = { elem: a( 'modernizr' ) }; Modernizr._q.push( function() {
        delete P.elem;
    }); var j = { style: P.elem.style }; Modernizr._q.unshift( function() {
    delete j.style;
}); var z = E._config.usePrefixes ? N.toLowerCase().split( ' ' ) : []; E._domPrefixes = z, E.testAllProps = g, E.testAllProps = y, Modernizr.addTest( 'flexbox', y( 'flexBasis', '1px', !0 ) ), Modernizr.addTest( 'csstransforms', function() {
    return -1 === navigator.userAgent.indexOf( 'Android 2.' ) && y( 'transform', 'scale(1)', !0 );
}); var k = 'CSS' in e && 'supports' in e.CSS, $ = 'supportsCSS' in e; Modernizr.addTest( 'supports', k || $ ), Modernizr.addTest( 'csstransforms3d', function() {
    var e = !!y( 'perspective', '1px', !0 ), t = Modernizr._config.usePrefixes; if ( e && ( !t || 'webkitPerspective' in w.style ) ) {
        var n, r = '#modernizr{width:0;height:0}'; Modernizr.supports ? n = '@supports (perspective: 1px)' : ( n = '@media (transform-3d)', t && ( n += ',(-webkit-transform-3d)' ) ), n += '{#modernizr{width:7px;height:18px;margin:0;padding:0;border:0}}', T( r + n, function( t ) {
            e = 7 === t.offsetWidth && 18 === t.offsetHeight;
        });
    } return e;
}), Modernizr.addTest( 'preserve3d', function() {
    var t, n, r = e.CSS, o = !1; return r && r.supports && r.supports( '(transform-style: preserve-3d)' ) ? !0 : ( t = a( 'a' ), n = a( 'a' ), t.style.cssText = 'display: block; transform-style: preserve-3d; transform-origin: right; transform: rotateY(40deg);', n.style.cssText = 'display: block; width: 9px; height: 1px; background: #000; transform-origin: right; transform: rotateY(40deg);', t.appendChild( n ), w.appendChild( t ), o = n.getBoundingClientRect(), w.removeChild( t ), o = o.width && o.width < 4 );
}), T( '#modernizr { height: 50vh; }', function( t ) {
    var n = parseInt( e.innerHeight / 2, 10 ), r = parseInt( d( t, null, 'height' ), 10 ); Modernizr.addTest( 'cssvhunit', r == n );
}), T( '#modernizr { width: 50vw; }', function( t ) {
    var n = parseInt( e.innerWidth / 2, 10 ), r = parseInt( d( t, null, 'width' ), 10 ); Modernizr.addTest( 'cssvwunit', r == n );
}), o(), i( b ), delete E.addTest, delete E.addAsyncTest; for ( var F = 0; F < Modernizr._q.length; F++ ) {
    Modernizr._q[ F ]();
}e.Modernizr = Modernizr;
})( window, document );
