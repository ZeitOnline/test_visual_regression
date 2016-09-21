/**
 * @fileOverview jQuery Plugin for displaying image copyrights in footer
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
(function( $ ) {
    /**
    * See (http://jquery.com/)
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
    * toggle view of footer areas for mobile devices
    * @class extendFooter
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.imageCopyrightFooter = function() {

        var containerTemplate = $( '#image-copyright-template' ),
            itemTemplate = '<li class="image-copyright-footer__item">' +
                '<img class="image-copyright-footer__item-image" src="___image___" />' +
                '___name___' +
                '</li>',
            slideDuration = 300,
            scrollDuration = 500,
            copyrights = {
                container: null,
                initialized: false,
                open: false,

                toggle: function() {
                    if ( !this.initialized ) {
                        this.init();
                    }

                    if ( this.open ) {
                        this.hide();
                    } else {
                        this.show();
                    }
                },

                show: function() {
                    // there is a strange unresolvable bug that it's only scrolling on the first click
                    // or never at all when using Velocity for the sliding animation, so use jQuery instead
                    this.container
                        .slideDown({ duration: slideDuration });
                    //  .velocity( 'slideDown', slideDuration );
                    this.container.children().eq( 0 )
                        .scrollIntoView({ duration: scrollDuration });
                    this.open = true;
                },

                hide: function() {
                    this.container
                        .velocity( 'slideUp', slideDuration );
                    this.open = false;
                },

                init: function() {
                    var $imagesWithCopyright = $( 'figure' ),
                        i, l,
                        wholeString = '',
                        $currentImage,
                        $currentImageTag,
                        $currentCopyrightHolder,
                        currentImageUrl;

                    // TODO: This is too holprig!!
                    for ( i = 0, l = $imagesWithCopyright.length; i < l; i++ ) {
                        $currentImage = $imagesWithCopyright.eq( i );
                        $currentCopyrightHolder = $currentImage.find( '*[itemprop=copyrightHolder]' );

                        if ( !$currentCopyrightHolder.text() ) {
                            continue;
                        }

                        // Get image source URL. Consider unfetched lazy loading images.
                        $currentImageTag = $currentImage.find( 'img' ).eq( 0 );
                        currentImageUrl = $currentImageTag.data( 'source' ) || $currentImageTag.attr( 'src' );

                        // If no image was found, check if the copyright belongs t a video poster image
                        if ( !currentImageUrl ) {
                            currentImageUrl = $currentImage.find( '.vjs-poster' ).eq( 0 ).css( 'background-image' );
                            if ( currentImageUrl ) {
                                currentImageUrl = currentImageUrl.replace( /(url\(|\)|'|")/gi, '' );
                            }
                        }

                        // Add current image to the list (if successfull)
                        if ( currentImageUrl ) {
                            wholeString += itemTemplate
                                .replace( '___name___', $currentCopyrightHolder.html() )
                                .replace( '___image___', currentImageUrl );
                        }
                    }

                    containerTemplate.before( containerTemplate.html() );
                    $( '#image-copyright-items' ).html( wholeString );

                    $( '.js-image-copyright-footer-close' ).on( 'click', function( e ) {
                        e.preventDefault();
                        copyrights.hide();
                    } );

                    this.container = $( '#bildrechte' );
                    this.initialized = true;
                }
            };

        return this.each( function() {
            $( this ).on( 'click', function( e ) {
                e.preventDefault();
                copyrights.toggle();
            } );
        });
    };
})( jQuery );
