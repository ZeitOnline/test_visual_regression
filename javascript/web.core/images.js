/**
 * @fileOverview Module for responsive images
 * @version  0.2 (adds lazy loading features)
 */
/**
 * images.js: module for images
 * @module images
 */
define([ 'sjcl', 'jquery', 'web.core/zeit', 'jquery.debounce', 'jquery.throttle' ], function( sjcl, $, Zeit ) {

    var images = [],
        $w = $( window ),
        threshold = 300,
        proxyScreen = {
            breakpoint: Zeit.breakpoint.get(),
            width: $w.width()
        },
        devicePixelRatio = window.devicePixelRatio || 1,
        isMobile, isDesktop, $triggerRegion;

    /**
     * images.js: mimic ECMAScript 6 String.prototype.endsWith()
     * @function stringEndsWith
     * @param  {string} subjectString   haystack
     * @param  {string} searchString    needle
     */
    function stringEndsWith( subjectString, searchString ) {
        var position = subjectString.length - searchString.length,
            index = subjectString.indexOf( searchString, position );

        return index !== -1 && index === position;
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
     * images.js: initiate globals for module
     * @function prepareScaling
     */
    function prepareScaling() {
        var breakpoint = Zeit.breakpoint.get();

        isMobile = /mobile|phablet/.test( breakpoint );
        isDesktop = breakpoint === 'desktop';
    }

    /**
     * images.js: get width, height and source for one image
     * @function getImageData
     * @param  {object} image     jquery object with image
     * @return {object}           object with width, height, source
     */
    function getImageData( $img ) {
        prepareScaling();
        var image = $img.get( 0 ),
            $parent = $img.closest( '.scaled-image' ),
            imageData = $img.data(),
            useMobileVariant = isMobile && imageData.mobileRatio && imageData.mobileSrc,
            ratio = useMobileVariant ? imageData.mobileRatio : imageData.ratio,
            msieWidth = false,
            subject, width, height, origWidth, origHeight, leaf, styles, minHeight, maxHeight, source, token;

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
                leaf = subject;

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

            // to decrease the number of variants which are fetched from the
            // server, we use image width in steps of 50px on mobile
            // IMPORTANT: keep original width and height for returned object
            origWidth = Math.round( width );
            origHeight = Math.round( width / ratio );
            if ( !isDesktop ) {
                width = Math.ceil( width / 50 ) * 50;
            }

            height = width / ratio;

            // be carefull, css('max-height') gives you 'dd%' for invisible elements
            // and for elements with percent values in webkit/blink
            styles = $img.css([ 'min-height', 'max-height' ]);
            minHeight = styles[ 'min-height' ];
            minHeight = stringEndsWith( minHeight, 'px' ) ? parseFloat( minHeight ) : undefined;
            maxHeight = styles[ 'max-height' ];
            maxHeight = stringEndsWith( maxHeight, 'px' ) ? parseFloat( maxHeight ) : undefined;

            if ( minHeight && minHeight > height ) {
                width = minHeight * ratio;
                height = minHeight;
            } else if ( maxHeight && maxHeight < height ) {
                width = maxHeight * ratio;
                height = maxHeight;
            }
        }

        // source berechnen
        source = [];
        source.push(
            useMobileVariant ? imageData.mobileSrc : imageData.src,
            Math.round( width ) + 'x' + Math.round( height ),
            isMobile ? 'mobile' : 'desktop'
        );

        // only enabled for certain assets
        if ( $parent.hasClass( 'high-resolution' ) && devicePixelRatio > 1 ) {
            source.push( 'scale_' + devicePixelRatio );
        }

        return {
            width: origWidth,
            height: origHeight,
            source: source.join( '__' )
        };
    }

    /**
     * images.js: show one image by replaceing the src
     * @function showImage
     * @param  {object} $img jquery object with image
     */
    function showImage( $img ) {
        var imgData = $img.data();
        $img
            .data( 'loading', true )
            .data( 'tolazyload', false )
            .attr( 'src', imgData.source )
            .attr( 'alt', imgData.alt )
            .on( 'load', function() {
                $( this )
                    .removeClass( 'image--processing' )
                    .data( 'loading', false )
                    .data( 'loaded', true )
                    .removeAttr( 'width' )
                    .removeAttr( 'height' );
            });
    }

    /**
     * images.js: prepare one image for loading and/or lazy loading
     * @function prepareImage
     * @param  {object} $img           jquery object with img
     * @param  {Boolean} markLazyImages differ between direct and lazy loaded images
     * @return {object}                jquery object with img
     */
    function prepareImage( $img, markLazyImages ) {
        var imgData;
        // remove possible fallback source information
        $img.removeAttr( 'data-dev-null' );
        imgData = getImageData( $img );
        $img
            .attr( 'width', imgData.width )
            .attr( 'height', imgData.height )
            .data( 'source', imgData.source )
            .data( 'processed', true );
        // add blank.gif (really, it is) to prevent rendering of broken image icon, if there's no src
        $img.attr( 'src', function() {
            return $( this ).attr( 'src' ) || 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
        });
        // add event triggering to tell the world
        $img.on( 'load', function( e ) {
            $img.trigger( 'scaling_ready' );
        });
        if ( markLazyImages && $img.closest( '.cp-region' ).data( 'lazy' ) === true ) {
            $img.data( 'tolazyload', true );
        }
        return $img;
    }

    /**
     * images.js: take a bunch of images, prepare them for showing
     * @function showImages
     * @param  {array} imageArray  optional array of jQuery objects of images
     */
    function showImages( imageArray ) {
        imageArray = imageArray || $( images ).filter( function() {
            var $parent = $( this ).closest( '.scaled-image' );
            // fix for galleries, remove, if we want img galleries lazy
            if ( $( this ).closest( '.slide' ).length > 0 || $( this ).closest( '.photocluster__item' ).length > 0 ) {
                return true;
            }
            // if lazyload or hidden filter out
            if ( $( this ).data( 'tolazyload' ) === true || $parent.css( 'display' ) === 'none' ) {
                return false;
            }
            return true;
        });
        $( imageArray ).each( function() {
            var $img = $( this );
            if ( $img.data( 'toscale' ) ) {
                $img = prepareImage( $( this ) );
            }
            if ( $img.data( 'tolazyload' ) === true ) {
                $img.addClass( 'image--processing' );
            }
            showImage( $img );
        });
    }

    /**
     * images.js: filter function to check if an item is inview
     * called as jQuery filter, $( this ) is provided by jQuery.fn.filter
     * @function isInView
     * @return {Boolean}
     */
    function isInView() {
        var $parent = $( this ).closest( '.scaled-image' );
        if ( $( this ).data( 'loaded' ) === true || $( this ).data( 'loading' ) === true || $parent.css( 'display' ) === 'none' ) {
            return false;
        }
        var $element = $( this ),
            windowTop = $w.scrollTop(),
            windowBottom = windowTop + $w.height(),
            elementTop = $element.offset().top,
            elementBottom = elementTop + $element.height();

        return elementBottom >= windowTop - threshold && elementTop <= windowBottom + threshold;
    }

    /**
     * images.js: collect images in viewport and show them
     * event for unveiling lazy images
     */
    function showLazyImages() {
        var inview = $( images ).filter( isInView );
        if ( inview.length > 0 ) {
            showImages( inview );
        }
    }

    /**
     * images.js: prepare all images on the page for direct or lazy loading
     * @function prepareImages
     * @return {array}           Array of images
     */
    function prepareImages( container ) {
        var images = [];
        prepareScaling();
        $( '.scaled-image noscript', container ).each( function() {
            var $noscript = $( this ),
                $parent = $noscript.parent(),
                markup = $noscript.text(),
                imgData;

            if ( markup.trim() !== '' ) {
                // get rid of src attribute
                // otherwise the browser would load it when put into the DOM
                // markup = markup.replace( / src=('|')[^'']+\1/g, '' );
                // replace src-attr to prevent regex and remove it later
                markup = markup.replace( 'src="', 'data-dev-null="' );
                // hide alt from display while image is processed
                markup = markup.replace( 'alt="', 'data-alt="' );
                // hide remaining conditional comment fragments
                markup = markup.replace( '<!--<![endif]-->', '' );
                markup = markup.replace( '<!--[if gt IE 8]><!-->', '' );

                $noscript.replaceWith( markup );
                images.push( prepareImage( $parent.find( 'img' ), true ) );

            } else {
                // noscript tag contains no readable content (might happen in older browsers)
                // therefore we have to hide allocated image spaces
                hideImage( $parent, $noscript.attr( 'data-src' ) );
            }
        });
        return images;
    }

    /**
     * images.js: mark all images for rescale, rescale those in viewport
     * @function rescaleAll
     */
    function rescaleAll() {
        var oldBreakpoint = proxyScreen.breakpoint,
            oldWidth = proxyScreen.width;
        // mark actual screen env
        proxyScreen.breakpoint = Zeit.breakpoint.get();
        proxyScreen.width = $w.width();
        // only rescale if needed
        if ( proxyScreen.breakpoint !== oldBreakpoint || proxyScreen.width > oldWidth ) {
            $( images ).each( function() {
                $( this )
                    .data( 'loading', false )
                    .data( 'loaded', false )
                    .data( 'tolazyload', true )
                    .data( 'toscale', true );
            });
            var inview = $( images ).filter( isInView );
            if ( inview.length > 0 ) {
                showImages( inview );
            }
        }
    }

    /**
     * images.js: rescale a bunch of images, to be backwards compatible with old images.js
     * @function scaleImages
     * @param {object} [container] DOM node with images to scale
     */
    function scaleImages( container ) {
        prepareScaling();
        showImages( prepareImages( container ) );
    }

    /**
     * images.js: initialize images
     * @function init
     * @param  {object} options jQuery styled preferences object
     */
    function init( options ) {
        options = $.extend( {
            triggerRegionNumber: 3,
            lazy: $( 'body[data-page-type="centerpage"]' ).length > 0,
            lazyElementsSelector: '.cp-region'
        }, options );
        // if lazy, mark lazy regions
        if ( options.lazy ) {
            $( options.lazyElementsSelector + ':gt(' + ( options.triggerRegionNumber - 1 ) + ')' ).data( 'lazy', true );
        }
        images = prepareImages();
        showImages();
        $w.on( 'scroll.lazy', $.throttle( showLazyImages, 50 ) );
        showLazyImages();
        $w.on( 'resize.rescale', $.debounce( rescaleAll, 1000 ) );
    }

    return {
        scale: scaleImages,
        init: init
    };

});
