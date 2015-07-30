/**
 * @fileOverview Module an API for track events and clicks via webtrekk
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
define( [ 'jquery' ], function( $ ) {
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
                return trackElement.useDataId( $element );
            }

            // is this a link inside an article text? track this specific case.
            if ( $element.closest( '.article-page' ).length > 0 ) {
                return trackElement.linkInArticleContent( $element );
            }

            var data = [],
                type = 'text',
                teasertype = '',
                $article = $element.closest( 'article' ),
                articleClasses = $article.get( 0 ).className.split( ' ' );
            if ( $element.attr( 'class' ).indexOf( 'button' ) !== -1 ) {
                type = 'button';
            } else if ( $element.closest( 'figure' ).length > 0 ) {
                type = 'image';
            }
            teasertype += $article.data( 'meetrics' ) ? $article.data( 'meetrics' ) + '-' : '';
            teasertype += articleClasses[0];
            data = [
                getBreakpoint(),
                $element.closest( '.cp-region' ).index( '.main .cp-region' ) + 1, // region bzw. verortung
                $element.closest( '.cp-area' ).index() + 1, // area bzw. reihe
                $article.index() + 1, // module bzw. spalte
                teasertype, // subreihe
                type, // bezeichner (image, button, text)
                $element.attr( 'href' ) // url
            ];
            return formatTrackingData( data );
        },
        /**
         * track elements in the nav section section, i.e. links with data-id attribute that contains the complete webtrekk id
         * @param  {Object} $element jQuery Element with the link that was clicked
         * @return {string}          formatted linkId-string for webtrekk call
         */
        nav: function( $element ) {
            var data = [
                getBreakpoint(),
                $element.data( 'id' ),
                $element.attr( 'href' ) // url
            ];
            return formatTrackingData( data );
        },
        /**
         * track links with data-id attribute that contains the complete webtrekk id
         * @param  {Object} $element jQuery Element with the link that was clicked
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
                linkType = sanitizeString( $element.text().trim().toLowerCase() );
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
         * @param  {Object} $element jQuery Element with the link that was clicked
         * @return {string}          formatted linkId-string for webtrekk call
         */
        linkInArticleContent: function( $element ) {

            var $currentPage = $element.closest( '.article-page' ),
                $currentPageNumber = $currentPage.data( 'page-number' ) || 0,
                $allParagraphsOnPage = $currentPage.children( 'p' ),
                $currentParagraph = $element.closest( 'p' ),
                currentParagraphNumber = $allParagraphsOnPage.index( $currentParagraph ) + 1,
                data = [
                    getBreakpoint(),
                    'intext', // [verortung] Immer (intext)
                    currentParagraphNumber + '/seite-' + $currentPageNumber, // "Nummer des Absatzes"/"Nummer der Seite" Bsp: "2/seite-1"
                    '', // [spalte] leer lassen
                    '', // [subreihe] leer lassen
                    $element.text(), // [bezeichner] Verlinkter Text bsp. "Koalitionsverhandlungen sind gescheitert"
                    $element.attr( 'href' ) // url
                ];

            return formatTrackingData( data );
        }
    },
    clickTrack = function( event ) {
        if ( event.data.debug ) {
            event.preventDefault();
        }
        var trackingData = trackElement[ event.data.funcName ]( $( event.target ).closest( 'a' ) );
        if ( event.data.debug ) {
            console.debug( trackingData );
        }
        if ( trackingData ) {
            window.wt.sendinfo({
                linkId: trackingData,
                sendOnUnload: 1
            });
        }
    },
    formatTrackingData = function( trackingData ) {
        var url = trackingData.pop();
        if ( url ) {
            url = url.replace( /http(s)?:\/\//, '' );

            // For sharing links, we want to preserve the GET parameters.
            // Otherwise, remove them!
            if ( typeof( trackingData[1] ) !== 'string' || trackingData[1].indexOf( '.social.' ) === -1 ) {
                url = url.split( '?' )[0];
            }
        }
        return trackingData.join( '.' ) + '|' + url;
    },
    /**
     * returns the current breakpoint, and replaces "desktop" with "stationaer"
     * @return {string}          breakpoint for webtrekk
     */
    getBreakpoint = function() {
        return window.ZMO.breakpoint.value === 'desktop' ? 'stationaer' : window.ZMO.breakpoint.value;
    },
    /**
     * returns a string that is webtrekk-safe
     * @param  {string}     string from
     * @return {string}     string that only contains characters, numbers and minus
     */
    sanitizeString = function( str ) {
        return str.
            replace( 'ä', 'ae' ).
            replace( 'ö', 'oe' ).
            replace( 'ü', 'ue' ).
            replace( 'Ä', 'Ae' ).
            replace( 'Ö', 'Oe' ).
            replace( 'Ü', 'Ue' ).
            replace( 'ß', 'ss' ).
            replace( '_', '-' ).
            replace( /[^A-Za-z0-9\-]/g, '' );
    },
    /**
     *
     */
    registerGlobalTrackingMessageEndpointForVideoPlayer = function() {

        $( window ).on( 'message', function( event ) {

            var messageData,
                messageSender,
                eventString,
                $videoArticle,
                videoSeries = '',
                videoProvider = '',
                videoSize = '',
                videoPageUrl = '',
                data,
                trackingData;

            try {
                messageData = JSON.parse( event.originalEvent.data );
            } catch ( e ) {
                return;
            }

            if ( typeof( messageData.sender ) !== 'string' || typeof( messageData.message ) !== 'string' ) {
                return;
            }

            if ( messageData.sender !== 'videojsWebtrekk' ) {
                return;
            }

            eventString = messageData.message;

            $videoArticle = $( '.video-player' ).closest( 'article' );
            if ( $videoArticle.length > 0 ) {
                videoSeries = $videoArticle.data( 'video-series' ) || '';
                videoProvider = $videoArticle.data( 'video-provider' ) || '';
                videoSize = $videoArticle.data( 'video-size' ) || '';
                videoPageUrl = $videoArticle.data( 'video-page-url' ) || '';
            }

            data = [
                getBreakpoint(),
                'video',
                videoSize,
                videoSeries,
                videoProvider,
                '', // origin (zdf/reuters)
                eventString,
                videoPageUrl.replace( /http(s)?:\/\//, '' )
            ];
            trackingData = formatTrackingData( data );

            window.wt.sendinfo({
                linkId: trackingData,
                sendOnUnload: 1
            });

        });
    };

    return {
        init: function() {
            if ( typeof window.ZMO === 'undefined' || typeof window.wt === 'undefined' ) {
                return;
            }
            /**
             * trackingLinks - a collection of jQuery-Objects to add trackElement to.
             * The keys represent the trackElement type, so add new types, or add to jQuery-Collection if type is already in use
             *
             * @type Object
             */
            var trackingLinks = {
                main: $( '.main article a' ).not( '[data-wt-click]' ),
                nav: $( '.main_nav a[data-id], .footer a[data-id]' ).not( '[data-wt-click]' ),
                useDataId: $( '#snapshot a[data-id], #servicebox a[data-id], .article-interactions a[data-id]' ).not( '[data-wt-click]' ),
                parquetMeta: $( '.parquet-meta a' ).not( '[data-wt-click]' )
            };
            // The key name is used for calling the corresponding function in this.tracking
            for ( var key in trackingLinks ) {
                if ( trackingLinks.hasOwnProperty( key ) ) {
                    trackingLinks[ key ].on( 'click', {
                        funcName: key,
                        debug: document.location.href.indexOf( '?webtrekk-clicktracking-debug' ) > -1 || false
                    }, clickTrack );
                }
            }

            registerGlobalTrackingMessageEndpointForVideoPlayer();
        }
    };
});
