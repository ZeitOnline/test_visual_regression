/**
 * @fileOverview Module for responsive images
 * @version  0.1
 */
/**
 * images.js: module for images
 * @module images
 */
define([ 'sjcl', 'jquery', 'jquery.debounce' ], function( sjcl, $ ) {

    var images = [],

    /**
     * images.js: create prefix
     * @function prefix
     * @param  {integer} width width of image
     * @param  {integer} height height of image
     * @return {string} prefix string for image path
     */
    prefix = function( width, height ) {
        var key = width + ':' + height + ':time',
            out = sjcl.hash.sha1.hash( key ),
            digest = sjcl.codec.hex.fromBits( out );

        return '/bitblt-' + width + 'x' + height + '-' + digest;
    },

    /**
     * images.js: use standard image or hide allocated image spaces and
     * comments if noscript has no content
     * @function hideImages
     * @param  {object} imageWrapper image area containing noscript
     * @param  {string} altSource alternative image source
     */
    hideImages = function( $imageWrapper, altSource ) {
        if ( altSource ) {
            $imageWrapper.html( '<img src="' + altSource + '"/>' );
        } else {
            $imageWrapper.height( 'auto' );
            // OPTIMIZE: we should hide things inside the $imageWrapper,
            // but not all comment count on the whole page
            $( '.cp_comment__count__wrap' ).hide();
        }
    },

    /**
     * images.js: rescale one image
     * @function rescaleOne
     * @param  {object} image image object
     */
    rescaleOne = function( image ) {
        var $img = $( image ),
            $parent = $img.closest( '.scaled-image' ),
            ratio = $img.data( 'ratio' ),
            msieWidth = false,
            width, height, token, source, subject,
            styles, minHeight, maxHeight;

        if ( $parent.hasClass( 'is-pixelperfect' ) ) {
            // use explicit width and height from parent
            width  = $parent.width();
            height = $parent.innerHeight();
        } else {
            // the element to measure
            subject = $parent;

            // determine size of image from container width + ratio of original image
            width = subject.width();

            // workaround for hidden images
            if ( !subject.is( ':visible' ) ) {
                var leaf = subject;

                do {
                    if ( leaf.prop( 'hidden' ) ) {
                        leaf.prop( 'hidden', false ).css( 'display', 'block' );
                        width = subject.width();
                        leaf.prop( 'hidden', true ).css( 'display', '' );
                    } else if ( leaf.css( 'display' ) === 'none' ) {
                        leaf.css( 'display', 'block' );
                        width = subject.width();
                        leaf.css( 'display', '' );
                    }

                    leaf = leaf.parent();

                    if ( leaf.is( ':visible' ) ) {
                        break;
                    }
                } while ( leaf[0].nodeName !== 'BODY' );
            }

            // ie workarround to detect auto width
            if ( image.currentStyle ) {
                msieWidth = image.currentStyle.width;
            }

            // workaround for width = 'auto'
            if ( !width || msieWidth === 'auto' ) {
                width = $img.width( '100%' ).width();
                $img.width( '' );
            }

            height = width / ratio;

            // be carefull, this would give 'dd%' for invisible elements
            if ( $img.is( ':visible' ) ) {
                styles = $img.css([ 'min-height', 'max-height' ]);
                minHeight = parseFloat( styles[ 'min-height' ] );
                maxHeight = parseFloat( styles[ 'max-height' ] );

                if ( minHeight && minHeight > height ) {
                    width = minHeight * ratio;
                    height = minHeight;
                } else if ( maxHeight && maxHeight < height ) {
                    width = maxHeight * ratio;
                    height = maxHeight;
                }
            }
        }

        token = prefix( Math.round( width ), Math.round( height ) );
        source = image.src || $img.data( 'src' );
        image.src = source.replace( /\/bitblt-\d+x\d+-[a-z0-9]+/, token );
    },

    /**
     * images.js: rescale all images
     * @function rescaleAll
     * @param  {object} e event object
     */
    rescaleAll = function( e ) {
        if ( !e ) {
            // initial case, no images there yet, so create them
            $( '.scaled-image > noscript' ).each( function() {
                var $noscript = $( this ),
                    $parent = $noscript.parent(),
                    markup = $noscript.text();

                if ( markup.trim() !== '' ) {

                    markup = markup.replace( 'src="', 'data-src="' );
                    $parent.html( markup );
                    var $imgs = $parent.find( 'img' ),
                        width = 0,
                        height = 0;

                    $imgs.each( function() {
                        var $img = $( this );

                        // add event triggering to tell the world
                        $img.on( 'load', function( e ) {
                            $img.trigger( 'scaling_ready' );
                        });

                        rescaleOne( this );

                        images.push( this );
                    });

                } else {
                    // noscript doesn't has any content we can read (might happen in older browsers)
                    // therefore we have to hide allocated image spaces
                    hideImages( $parent, $noscript.attr( 'data-src' ));
                }

            });
        } else {
            // rescale after resize, images already set up, just update
            for ( var i = images.length; i--; ) {
                rescaleOne( images[i] );
            }
        }
    },

    /**
     * images.js: init scaling
     * @function init
     */
    init = function() {
        rescaleAll();

        $( window ).on( 'resize', $.debounce( rescaleAll, 1000 ) );
    };

    return {
        init: init
    };

});
