/**
 * @fileOverview Module and API for track events and clicks via webtrekk
 * @author moritz.stoltenburg@zeit.de, thomas.puppe@zeit.de
 * @version  0.1
 */
define( [ 'jquery', 'web.core/zeit' ], function( $, Zeit ) {

    var debugMode = document.location.hash.indexOf( 'debug-clicktracking' ) > -1;

    function formatTrackingData( trackingData ) {
        var length = trackingData.unshift( Zeit.breakpoint.getTrackingBreakpoint() ),
            url = trackingData.pop(),
            slug = trackingData.join( '.' );

        if ( url ) {
            url = url.replace( /http(s)?:\/\//, '' );

            // For some links, we want to preserve the GET parameters.
            // Otherwise, remove them!
            if ( slug.indexOf( '.social.' ) !== -1 ) {
                url = $( 'meta[property="og:url"]' );
                url = url.length ?
                    url.attr( 'content' ).replace( /http(s)?:\/\//, '' ) :
                    window.location.host + window.location.pathname;
            } else if ( slug.indexOf( '.studiumbox.' ) === -1 ) {
                url = url.split( '?' )[0];
            }
        }
        return slug + '|' + url;
    }

    /**
     * returns a string that is webtrekk-safe
     * This code does the same as format_webtrekk in template-py
     * @param  {string}     string from
     * @return {string}     lowercase string that only contains alphanumeric characters and underscore
     */
    function sanitizeString( str ) {
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
            .toString()
            .toLowerCase()
            .replace( /\W/g, transliterate )
            .replace( /_+/g, '_' )
            .replace( /^_|_$/g, '' );
    }

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

            // in case we are inside a data-ct-area element, this is redundant
            // e.g. ZEIT Campus sharing links
            if ( $element.closest( '[data-ct-area]' ).length ) {
                return;
            }

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
            teasertype += $article.data( 'zplus' ) ? '-zplus' : '';

            if ( element.type === 'submit' ) {
                href = element.form.action + '?' + $( element.form ).serialize();
                type = sanitizeString( element.value );
            } else {
                href = $element.attr( 'href' );
            }

            data = [
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
                $element.data( 'id' ),
                $element.attr( 'href' ) // url
            ];
            return formatTrackingData( data );
        },
        /**
         * track links inside parents with appropriate data attributes
         * @param  {object} $element jQuery collection with the link that was clicked
         * @return {string}          formatted linkId-string for webtrekk call
         */
        useDataArea: function( $element, event ) {
            var $area = $( event.delegateTarget ),
                $row = $element.closest( '[data-ct-row]' ),
                row = $row.data( 'ct-row' ),
                $column = $element.closest( '[data-ct-column]', $row ),
                column = $column.data( 'ct-column' ),
                subcolumn = '',
                $needle = $element,
                url,
                data;

            if ( $column.length && column !== false ) {
                // try to inherit parent value if no value is set (check for any number or string value)
                if ( column.length === 0 ) {
                    column = undefined;
                    $needle = $column.parent().find( 'a' ).first();
                }

                // only set subcolumn if not marked to be omitted
                if ( $column.data( 'ct-subcolumn' ) !== false ) {
                    subcolumn = $column.find( 'a' ).index( $element ) + 1 || 1;
                }
            }

            if ( column === undefined ) {
                if ( $area.is( $row ) || $area.find( '[data-ct-row="' + row + '"]' ).length === 1 ) {
                    // area and row attribute are on the same element
                    // or there is only one child row with that value
                    column = $row.find( 'a' ).not(
                        $row.find( '[data-ct-column] a' ) ).index( $needle ) + 1 || 1;
                } else {
                    // needed, if there are more containers with the same row value
                    column = $area.find( '[data-ct-row="' + row + '"] a' ).not(
                        $area.find( '[data-ct-column] a' ) ).index( $needle ) + 1 || 1;
                }
            } else if ( column === false ) {
                column = '';
            }

            if ( $element.attr( 'aria-controls' ) ) {
                // special treatment for one ZEIT Campus menu link >:(
                if ( !( Zeit.isMobileView() && $element.data( 'follow-mobile' ) ) ) {
                    url = '#' + $element.attr( 'aria-controls' );
                }
            } else if ( $element.attr( 'type' ) === 'submit' ) {
                url = $element.get( 0 ).form.action;
            } else {
                url = $element.attr( 'href' );
            }

            data = [
                $area.data( 'ct-area' ), // verortung
                row, // reihe
                column, // spalte
                subcolumn, // subreihe
                sanitizeString(
                    $element.data( 'ct-label' ) ||
                    $.trim( $element.contents().first().text() ) ||
                    $element.children().first().text() ||
                    $element.text() ), // bezeichner
                url // url
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
        var trackingData = trackElement[ event.data.funcName ]( $( this ), event );

        if ( debugMode ) {
            event.preventDefault();
            event.stopImmediatePropagation();
            console.debug( trackingData + ' (method: ' + event.data.funcName + ')' );
            window.trackingData = trackingData;
        } else if ( trackingData ) {
            window.wt.sendinfo({
                linkId: trackingData,
                sendOnUnload: 1
            });
        }
    };

    return {
        formatTrackingData: formatTrackingData,
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
                         '.section-heading',
                         '.section-footer',
                         '.snapshot__media',
                         '#servicebox',
                         '.breaking-news-banner',
                         '.article-lineage',
                         '.js-truncate-region',
                         '.partnerbox'
                        ].join(),
                        'a[data-id]:not([data-wt-click])'
                    ],
                    useDataArea: [
                        '[data-ct-area]',
                        [
                        'a:not([data-wt-click])',
                        'input[type="submit"]'
                        ].join()
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
