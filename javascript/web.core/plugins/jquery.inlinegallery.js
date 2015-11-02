/* global $blocked, WebKitCSSMatrix */

/**
 * @fileOverview jQuery Plugin for Inline-Gallery
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
(function( $, Modernizr ) {
    /**
     * See (http://jquery.com/).
     * @name jQuery
     * @alias $
     * @class jQuery Library
     * See the jQuery Library  (http://jquery.com/) for full details.  This just
     * documents the function and classes that are added to jQuery by this plug-in.
     */
    /**
     * See (http://jquery.com/)
     * @name fn
     * @class jQuery Library
     * See the jQuery Library  (http://jquery.com/) for full details.  This just
     * documents the function and classes that are added to jQuery by this plug-in.
     * @memberOf jQuery
     */
    /**
     * Prepares the inline gallery and adds some extra features
     * @class inlinegallery
     * @memberOf jQuery.fn
     * @param  {object} defaults configuration object, overwriting presetted options
     * @return {object} jQuery-Object for chaining
     */
    $.fn.inlinegallery = function( defaults ) {

        var hasTouch = Modernizr.touchevents || location.search === '?touch',
            options = $.extend({
                onSlideAfter: function() {
                    // integrate tracking
                    if ( 'clickCount' in window ) {
                        window.clickCount.webtrekk( 'hp.zm.slidegallery.showslide.' );
                        window.clickCount.ga( 'hp.zm.slidegallery.showslide.' );
                    }
                },
                slideSelector: '.slide',
                controls: !hasTouch,
                pagerType: ( hasTouch ) ? 'full' : 'short',
                nextText: 'Zum nächsten Bild',
                prevText: 'Zum vorigen Bild',
                infiniteLoop: true,
                hideControlOnEnd: false,
                adaptiveHeight: true
            }, defaults ),
            singleGallery = null,
            ressort = window.ZMO.view.ressort,
            viewType = window.ZMO.view.type,
            galleryType = /[\\?&]gallery=([^&#]*)/.exec( location.search ),
            query = /slide=(\d+)/.exec( location.search.slice( 1 ) ),
            start;

        if ( galleryType ) {
            galleryType = galleryType[1];
        }

        if ( query ) {
            if ( ( start = parseInt( query[1], 10 ) ) > 1 ) {
                options.startSlide = start - 1;
            }
        }

        if ( this.length && !window.ZMO.isMobileView() && galleryType !== 'dynamic' ) {
            $.ajax({
                url: window.ZMO.jsconfHost + '/gallery.blocked.ressorts.js',
                dataType: 'script',
                success: function() {
                    var queryString = location.search.slice( 1 ).replace( /&*\bslide=(\d+)/g, '' ),
                        isStatic = $.inArray( ressort, $blocked ) > -1 || /gallery=static/.test( queryString );

                    if ( singleGallery && isStatic ) {
                        singleGallery.goToSlide = function( slideIndex, direction ) {
                            var total = singleGallery.getSlideCount(),
                                next = ( total + slideIndex ) % total,
                                search = '',
                                prefix = '?';

                            if ( queryString ) {
                                search = '?' + queryString;
                                prefix = '&';
                            }

                            if ( next ) {
                                search += prefix + 'slide=' + ( next + 1 );
                            }

                            location.search = search;
                        };
                    }
                }
            });
        }

        // check if any part of the element is inside viewport
        var isElementInViewport = function( el ) {

            // special bonus for those using jQuery
            if ( el instanceof jQuery ) {
                el = el[0];
            }

            if ( !el.getBoundingClientRect ) {
                return false;
            }

            var rect = el.getBoundingClientRect(),
                windowWidth  = window.innerWidth  || document.documentElement.clientWidth,  /* or $( window ).width()  */
                windowHeight = window.innerHeight || document.documentElement.clientHeight; /* or $( window ).height() */

            return !(
                rect.top > windowHeight ||
                rect.bottom < 0 ||
                rect.left > windowWidth ||
                rect.right < 0
            );
        };

        return this.each( function() {
            var gallery = $( this ),
                galleryWidth = gallery.width(),
                figures = gallery.find( options.slideSelector ),
                figcaptions = gallery.find( '.figure__caption' ),
                backButton = $( '<div class="bx-zone-prev"><a class="bx-overlay-prev icon-pfeil-links">Ein Bild zurück</a></div>' ),
                nextButton = $( '<div class="bx-zone-next"><a class="bx-overlay-next icon-pfeil-rechts">Ein Bild vor</a></div>' ),
                buttons = backButton.add( nextButton ),
                DOM_VK_LEFT = 37,
                DOM_VK_RIGHT = 39,
                slider = {},
                sliderViewport,
                mq,
                handleKeydown = function( e ) {
                    // enable keyboard navigation
                    // do nothing if there is another key involved
                    if ( e.altKey || e.shiftKey || e.ctrlKey || e.metaKey ) { return; }

                    switch ( e.keyCode ) {
                        case DOM_VK_RIGHT:
                            if ( isElementInViewport( sliderViewport ) ) {
                                slider.goToNextSlide();
                            }
                            break;
                        case DOM_VK_LEFT:
                            if ( isElementInViewport( sliderViewport ) ) {
                                slider.goToPrevSlide();
                            }
                            break;
                    }
                };

            $( window ).on( 'keydown', handleKeydown );

            figures.on( 'scaling_ready', function( e ) {
                var currentSlide;

                figCaptionSize( $( e.target ) );

                // if the slider loaded before the image
                if ( slider.getCurrentSlideElement ) {
                    currentSlide = slider.getCurrentSlideElement();
                    // if loaded image is inside current active slide
                    if ( currentSlide.get( 0 ) === this ) {
                        // adjust height if necessary
                        if ( sliderViewport && sliderViewport.height() < currentSlide.height() ) {
                            sliderViewport.height( currentSlide.height() );
                        }
                    }
                }
            });

            var hideOverlays = function() {
                buttons.hide();
                figures.on( 'click', function() {
                    buttons.toggle();
                });
            };

            if ( window.matchMedia && !hasTouch ) {
                mq = window.matchMedia( '(max-width: 576px)' );

                if ( mq.matches ) {
                    hideOverlays();
                }

                mq.addListener( function() {
                    if ( mq.matches ) {
                        hideOverlays();
                    } else {
                        buttons.show();
                        figures.off( 'click' );
                    }
                });
            }

            var figCaptionSize = function( image, figcaption ) {
                    var caption = figcaption || image.closest( 'figure' ).find( 'figcaption' ),
                        imageWidth = image.width();

                    if ( caption.length && imageWidth > 30 && imageWidth < galleryWidth ) {
                        caption.css({
                            'max-width': imageWidth + 'px',
                            'padding-left': 0,
                            'padding-right': 0
                        });
                    }
                },
                figCaptionSizing = function() {
                    figcaptions.each( function() {
                        var caption = $( this ),
                            image = caption.prev().find( '.figure__media' );

                        figCaptionSize( image, caption );
                    });
                };

            options.onSliderLoad = function() {

                // TODO: has to be fixed, it isn't working but leads to a neverending loop
                // check for iOS bug not setting position correctly
                // if ( 'WebKitCSSMatrix' in window ) {
                //     var matrix = new WebKitCSSMatrix( gallery.css('transform') );

                //     // bxSlider got the position of the first slide wrong,
                //     // because the cloned last slide did not load until now
                //     if ( matrix.m41 === 0 ) {
                //         gallery.find( '.bx-clone img' ).eq( 0 ).on( 'load', function( e ) {
                //             $( this ).off( 'e' );
                //             slider.reloadSlider();
                //         });
                //     }
                // }

                figCaptionSizing();

                sliderViewport = gallery.parent();

                if ( !hasTouch ) {
                    /* additional buttons on image */
                    nextButton.insertAfter( gallery ).on( 'click', function() { slider.goToNextSlide(); } );
                    backButton.insertAfter( gallery ).on( 'click', function() { slider.goToPrevSlide(); } );

                    /* add icons to existing gallery buttons */
                    $( '.bx-next' ).addClass( 'icon-pfeil-rechts' );
                    $( '.bx-prev' ).addClass( 'icon-pfeil-links' );

                    sliderViewport.parent().addClass( 'bx-wrapper--no-touch' );
                } else {
                    sliderViewport.parent().addClass( 'bx-wrapper--touch' );
                }

                // fix ad columns
                $( '#iqdBackgroundLeft, #iqdBackgroundRight' ).css( { height: document.body.offsetHeight + 'px' } );

            };

            options.onSliderResize = function() {
                galleryWidth = gallery.width();
            };

            slider = gallery.bxSlider( options );

            // make element available for AJAX response
            if ( viewType === 'gallery' ) {
                singleGallery = slider;
            }
        });
    };
})( jQuery, window.Modernizr );
