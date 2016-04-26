/**
 * @fileOverview Module and API for track events and clicks via webtrekk
 * @author moritz.stoltenburg@zeit.de, thomas.puppe@zeit.de
 * @version  0.1
 */
define( [ 'jquery', 'web.core/zeit' ], function( $, Zeit ) {
    /**
     * trackElement - collection of the different functions to gather the needed info to track smth
     * @type {Object}
     */
    var trackElement = {
        /**
         * track elements in the main section
         * @param  {Object} $element jQuery Element with the link that was clicked
         * @return {string}          formatted linkId-string for webtrekk call
         */
        main: function( $element ) {

            // in case we already have a complete ID, we do not need to calculate it
            if ( $element.data( 'id' ) ) {
                return this.useDataId( $element );
            }

            // is this a link inside an article text? track this specific case.
            var $page = $element.closest( '.main--article .article-page' );
            if ( $page.length ) {
                return this.linkInArticleContent( $element, $page );
            }

            // is this a link inside a gallery? track this specific case.
            var $gallery = $element.closest( '.main--gallery .article-page' );
            if ( $gallery.length ) {
                return this.linkInGalleryContent( $element, $gallery );
            }

            var data = [],
                href,
                type = 'text',
                teasertype = '',
                element = $element.get( 0 ),
                $article = $element.closest( 'article, aside' ),
                $area = $element.closest( '.cp-area' ),
                articleClasses = $article.get( 0 ).className.split( ' ' );

            if ( element.className.indexOf( 'button' ) !== -1 ) {
                type = 'button';
            } else if ( $element.closest( 'figure' ).length ) {
                type = 'image';
            }

            teasertype += $article.data( 'clicktracking' ) ? $article.data( 'clicktracking' ) + '-' : '';
            teasertype += articleClasses[0];

            if ( element.type === 'submit' ) {
                href = element.form.action + '?' + $( element.form ).serialize();
                type = sanitizeString( element.value );
            } else {
                href = $element.attr( 'href' );
            }

            data = [
                getBreakpoint(),
                $element.closest( '.cp-region' ).index( '.main .cp-region' ) + 1, // region bzw. verortung
                $area.index() + 1, // area bzw. reihe
                $area.find( 'article, aside' ).index( $article ) + 1, // module bzw. spalte
                teasertype, // subreihe
                type, // bezeichner (image, button, text)
                href // url
            ];

            return formatTrackingData( data );
        },
        /**
         * track links with data-id attribute that contains the complete webtrekk id without href
         * @param  {object} $element jQuery collection with the link that was clicked
         * @return {string}          formatted linkId-string for webtrekk call
         */
        useDataId: function( $element ) {
            var data = [
                getBreakpoint(),
                $element.data( 'id' ),
                $element.attr( 'href' ) // url
            ];
            return formatTrackingData( data );
        },
        /**
         * track links with data-tracking attribute that contains the complete webtrekk id plus href
         * @param  {object} $element jQuery collection with the link that was clicked
         * @return {string}          formatted linkId-string for webtrekk call
         */
        useDataTracking: function( $element ) {
            var trackingData = $element.data( 'tracking' ).split( '|' ),
                data = [
                    getBreakpoint(),
                    trackingData[0],
                    trackingData[1] // url
                ];
            return formatTrackingData( data );
        },
        /**
         * track elements in the parquet-meta section
         * definition: https://docs.google.com/spreadsheets/d/1uY8XXULPq7zUre9prBWiKDaBQercLmAEENCVF8LQk4Q/edit#gid=1056411343
         * @param  {Object} $element jQuery Element with the link that was clicked
         * @return {string}          formatted linkId-string for webtrekk call
         */
        parquetMeta: function( $element ) {

            var linkClassName = $element.get( 0 ).className.split( ' ' )[0],
                linkType,
                data;

            if ( linkClassName === 'parquet-meta__title' ) {
                linkType = sanitizeString( $element.text() );
            } else {
                linkType = linkClassName.split( '__' ).pop().replace( '-', '' );
            }

            data = [
                getBreakpoint(),
                'parquet', // Verortung
                $element.index( '.parquet-meta a' ) + 1, // Reihe (insgesamt, nicht aktueller Riegel)
                '1', // Spalte
                '', // Teasertyp, hier leer
                linkType, // Name (bei Ressort) oder Linktyp (politik|wirtschaft / topiclink|morelink)
                $element.attr( 'href' ) // Ziel-URL
            ];

            return formatTrackingData( data );
        },
        /**
         * track links which are inside an article text
         * @param  {object} $element jQuery collection with the link that was clicked
         * @param  {object} $page    jQuery collection with the page containing the clicked link
         * @return {string}          formatted linkId-string for webtrekk call
         */
        linkInArticleContent: function( $element, $page ) {
            var $currentParagraph =  $element.closest( 'p, [data-clicktracking]', $page ),
                currentPageNumber = $page.data( 'page-number' ) || 0,
                currentParagraphNumber = $currentParagraph.prevAll( 'p' ).length + 1,
                trackType = $element.closest( '[data-clicktracking]' ).data( 'clicktracking' ) || 'intext',
                data = [
                    getBreakpoint(),
                    trackType, // [verortung]
                    currentParagraphNumber + '/seite-' + currentPageNumber, // "Nummer des Absatzes"/"Nummer der Seite" Bsp: "2/seite-1"
                    '', // [spalte] leer lassen
                    '', // [subreihe] leer lassen
                    sanitizeString( $element.text() ), // [bezeichner] Verlinkter Text bsp. "koalitionsverhandlungen_sind_gescheitert"
                    $element.attr( 'href' ) // url
                ];

            return formatTrackingData( data );
        },

        linkInGalleryContent: function( $element, $gallery ) {
            var imgnumber = $gallery.find( '.bx-pager' ).text().split( ' / ' )[0],
                data = [
                    getBreakpoint(),
                    'gallery', // [verortung]
                    $element[ 0 ].className.indexOf( 'overlay' ) < 0 ? '1' : '2',
                    $element[ 0 ].className.indexOf( 'links' ) < 0 ? '2' : '1', // [spalte]
                    imgnumber, // [subreihe]
                    sanitizeString( $element.text() ), // [bezeichner]
                    window.location.href // url
                ];
            return formatTrackingData( data );
        }
    },
    clickTrack = function( event ) {
        var trackingData = trackElement[ event.data.funcName ]( $( this ) );

        if ( debugMode ) {
            event.preventDefault();
            event.stopImmediatePropagation();
            console.debug( trackingData );
        } else if ( trackingData ) {
            window.wt.sendinfo({
                linkId: trackingData,
                sendOnUnload: 1
            });
        }
    },
    formatTrackingData = function( trackingData ) {
        var url = trackingData.pop(),
            slug = trackingData.join( '.' );

        if ( url ) {
            url = url.replace( /http(s)?:\/\//, '' );

            // For some links, we want to preserve the GET parameters.
            // Otherwise, remove them!
            if ( !/\.(social|studiumbox)\./.test( slug ) ) {
                url = url.split( '?' )[0];
            }
        }
        return slug + '|' + url;
    },
    /**
     * returns the current breakpoint
     * @return {string}          breakpoint for webtrekk
     */
    getBreakpoint = function() {
        return Zeit.breakpoint.getTrackingBreakpoint();
    },
    /**
     * returns a string that is webtrekk-safe
     * This code does the same as format_webtrekk in template-py
     * @param  {string}     string from
     * @return {string}     lowercase string that only contains alphanumeric characters and underscore
     */
    sanitizeString = function( str ) {
        var map = {
                'ä': 'ae',
                'ö': 'oe',
                'ü': 'ue',
                'á': 'a',
                'à': 'a',
                'é': 'e',
                'è': 'e',
                'ß': 'ss'
            },
            transliterate = function( m ) {
                return map[m] || '_';
            };

        return str
            .toLowerCase()
            .replace( /\W/g, transliterate )
            .replace( /_+/g, '_' )
            .replace( /^_|_$/g, '' );
    },

    debugMode = document.location.hash.indexOf( 'debug-clicktracking' ) > -1;

    return {
        init: function() {
            if ( typeof Zeit === 'undefined' || ( typeof window.wt === 'undefined' && !debugMode ) ) {
                return;
            }
            /**
             * trackingLinks - a collection of jQuery-Objects to add trackElement to.
             *
             * The keys represent the trackElement type, so add new types, or add to
             * jQuery collection if type is already in use.
             * The values are a list of delegates for event handling and optional selector strings
             * to filter the descendants of the selected elements that trigger the event.
             */
            var trackingLinks = {
                    main: [
                        '.main',
                        [
                         'article a:not([data-wt-click])',
                         'aside a:not([data-wt-click])',
                         'aside input[type="submit"]'
                        ].join()
                    ],
                    useDataId: [
                        [
                         '.main_nav',
                         '.header__tags',
                         '.footer',
                         '.article-interactions',
                         '.article-tags',
                         '.section-heading',
                         '.snapshot__media',
                         '#servicebox',
                         '.breaking-news-banner',
                         '.article-lineage',
                         '.partnerbox',
                         '.header', // campus navi
                         '.main-nav' // zmo navi
                        ].join(),
                        'a[data-id]:not([data-wt-click])'
                    ],
                    parquetMeta: [
                        '.parquet-meta',
                        'a:not([data-wt-click])'
                    ]
                };

            // The key name is used for calling the corresponding function in trackElement
            for ( var key in trackingLinks ) {
                if ( trackingLinks.hasOwnProperty( key ) ) {
                    var selectors = trackingLinks[ key ],
                        delegate = selectors.shift(),
                        filter = selectors.shift() || null;

                    $( delegate ).on( 'click', filter, {
                        funcName: key
                    }, clickTrack );
                }
            }

            // exceptions and extra cases
            $( '*[data-tracking]' ).on( 'click', {
                funcName: 'useDataTracking'
            }, clickTrack );

        }
    };
});
