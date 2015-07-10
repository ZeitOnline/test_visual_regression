/**
 * @fileOverview Module for responsive images
 * @version  0.1
 */
/**
 * images.js: module for images
 * @module images
 */
define([ 'sjcl', 'jquery', 'jquery.debounce' ], function( sjcl, $ ) {

    var images = [];

    /**
     * images.js: create prefix
     * @function prefix
     * @param  {integer} width width of image
     * @param  {integer} height height of image
     * @return {string} prefix string for image path
     */
    function prefix( width, height ) {
        var key = width + ':' + height + ':time',
            out = sjcl.hash.sha1.hash( key ),
            digest = sjcl.codec.hex.fromBits( out );

        return '/bitblt-' + width + 'x' + height + '-' + digest;
    }

    /**
     * images.js: use standard image or hide allocated image space and
     * comment counter if no alternative source URL is present
     * @function hideImage
     * @param  {object} imageWrapper image area containing noscript
     * @param  {string} source alternative image source
     */
    function hideImage( $imageWrapper, source ) {
        if ( source ) {
            $imageWrapper.html( '<img src="' + source + '"/>' );
        } else {
            $imageWrapper.html( '' ).height( 'auto' );
            // @todo: we should hide things inside the $imageWrapper,
            // but not all comment count on the whole page
            // unfortunately comment count is outside of the $imageWrapper in ZMO
            $( '.cp_comment__count__wrap' ).hide();
        }
    }

    /**
     * images.js: scale one image
     * @function scaleImage
     * @param  {object} image HTMLImageElement
     */
    function scaleImage( image ) {
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
    }

    /**
     * images.js: scale contained images
     * @function scaleImages
     * @param  {object} container DOM element, array of elements or jQuery object
     *                            used as selector context, defaults to document root
     */
    function scaleImages( container ) {
        $( '.scaled-image > noscript', container ).each( function() {
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

                    scaleImage( this );

                    images.push( this );
                });

            } else {
                // noscript tag contains no readable content (might happen in older browsers)
                // therefore we have to hide allocated image spaces
                hideImage( $parent, $noscript.attr( 'data-src' ));
            }
        });
    }

    /**
     * images.js: scale all images in document
     * @function scaleAll
     */
    function scaleAll() {
        scaleImages();
    }

    /**
     * images.js: rescale all previously scaled images
     * @function rescaleAll
     */
    function rescaleAll() {
        for ( var i = images.length; i--; ) {
            // verify that image is still part of the DOM
            if ( $.contains( document.documentElement, images[i] )) {
                scaleImage( images[i] );
            } else {
                // remove the image reference
                images.splice( i, 1 );
            }
        }
    }

    /**
     * images.js: initialize image scaling
     * @function init
     */
    function init() {
        scaleAll();

        $( window ).on( 'resize', $.debounce( rescaleAll, 1000 ) );
    }

    return {
        scale: scaleImages,
        init: init
    };

});
