/**
 * @fileOverview WM-Ticker helper functions and init stuff
 * @author hennes.roemmer@zeit.de
 * @version  0.1
 */
function wmTicker( element ) {
    var defaults = {
        headline: 'FIFA WM 2018',
        dataURL: 'https://kickerticker.zeit.de/standings',
        dataPath: '?today=eq.true',
        webSocketURL: 'wss://ws.zeit.de:443/',
        webSocketPath: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.' +
        'eyJjaGFubmVsIjoid20iLCJtb2RlIjoiciJ9.' +
        'c791lyW1KxWajSmmmnHSjjR5hJPkGn2ZNSsQGG072WQ',
        detailLink: '',
        wsEnabled: false,
        refreshSeconds: 10,
        showRunningGameTime: true,
        countries: [
            { name: 'Russland', short: 'ru', long: 'rus' },
            { name: 'Saudi-Arabien', short: 'sa', long: 'ksa' },
            { name: 'Ägypten', short: 'eg', long: 'egy' },
            { name: 'Uruguay', short: 'uy', long: 'uru' },
            { name: 'Marokko', short: 'ma', long: 'mar' },
            { name: 'Iran', short: 'ir', long: 'irn' },
            { name: 'Portugal', short: 'pt', long: 'por' },
            { name: 'Spanien', short: 'es', long: 'esp' },
            { name: 'Frankreich', short: 'fr', long: 'fra' },
            { name: 'Australien', short: 'au', long: 'aus' },
            { name: 'Argentinien', short: 'ar', long: 'arg' },
            { name: 'Island', short: 'is', long: 'isl' },
            { name: 'Peru', short: 'pe', long: 'per' },
            { name: 'Dänemark', short: 'dk', long: 'den' },
            { name: 'Kroatien', short: 'hr', long: 'cro' },
            { name: 'Nigeria', short: 'ng', long: 'nga' },
            { name: 'Costa Rica', short: 'cr', long: 'crc' },
            { name: 'Serbien', short: 'rs', long: 'srb' },
            { name: 'Deutschland', short: 'de', long: 'ger' },
            { name: 'Mexiko', short: 'mx', long: 'mex' },
            { name: 'Brasilien', short: 'br', long: 'bra' },
            { name: 'Schweiz', short: 'ch', long: 'sui' },
            { name: 'Schweden', short: 'se', long: 'swe' },
            { name: 'Südkorea', short: 'kr', long: 'kor' },
            { name: 'Belgien', short: 'be', long: 'bel' },
            { name: 'Panama', short: 'pa', long: 'pan' },
            { name: 'Tunesien', short: 'tn', long: 'tun' },
            { name: 'England', short: 'gb-eng', long: 'eng' },
            { name: 'Kolumbien', short: 'co', long: 'col' },
            { name: 'Japan', short: 'jp', long: 'jpn' },
            { name: 'Polen', short: 'pl', long: 'pol' },
            { name: 'Senegal', short: 'sn', long: 'sen' }
        ]
    };

    // empty constructor to add functions to
    function WmTicker() {
        this.data = {};
        this.debug = location.hash.indexOf( 'debug-wm-ticker' ) > -1;
        this.init();
    }

    WmTicker.prototype.init = function() {
        this.debugHelper();
        this.setConfigurableAttributes();

        if ( this.debugLocally() ) {
            // mock response for local testing
            console.log( 'WM-TICKER: debugging locally with mocked response' );
            require([ 'web.site/wmTickerData' ], function( data ) {
                this.data = data;
                this.renderView();
            }.bind( this ) );
        } else {
            // initial GET Request
            this.fetchData();
            if ( defaults.wsEnabled ) {
                this.initWebSocket();
            } else {
                this.addFallbackInterval();
            }
        }

        // Update game time display every 10 seconds
        // => ONLY if game not finished or pre-match
        setInterval( this.updateTime.bind( this ), 10000 );
    };


    /**
     * check if Debugging is enabled
     * -> Changes WebSocket and Fallback URL
     */
    WmTicker.prototype.debugLocally = function() {
        // enable usage of a mock xhr response for stable testing
        return location.hash.indexOf( 'debug-wm-ticker-locally' ) > -1;
    };

    /**
     * build path string to set defaults.dataPath to
     * @param  {string | Date}  date received from data Attribute OR URL
     * @return {string} date Path to add to defaults.dataPath
     */
    WmTicker.prototype.pathString = function( date ) {
        var dateFrom = new Date( date ),
            dateTo = new Date( date );

        dateTo.setDate( dateFrom.getDate() + 1 );

        return '?date=gt.' + dateFrom.toISOString().substr( 0, 10 ) + '&date=lt.' + dateTo.toISOString().substr( 0, 10 );
    };

    /**
     * helper to set fixed test debug date
     * -> Changes WebSocket and Fallback URL
     */
    WmTicker.prototype.debugHelper = function() {
        // if data-date set use that! Else if debugEnabled, use that.
        // Data Attribute is prioritized!
        var dataDate = element.getAttribute( 'data-date' );
        if ( dataDate ) {
            defaults.dataPath = this.pathString( dataDate );
            console.log( 'WM-TICKER: Date set by DATA Attribute to: %s', dataDate );
        } else if ( this.debug ) {
            var url = new URL( window.location.href );
            var date = url.searchParams.get( 'date' );
            if ( date ) {
                defaults.dataPath = this.pathString( date );
                console.log( 'WM-TICKER: Date set to: %s', date );
            }
        }
    };

    /**
     * get DATA Attributes and set them in defaults object for later use
     */
    WmTicker.prototype.setConfigurableAttributes = function() {
        var backendURL = element.getAttribute( 'data-backend-url' ),
            detailLink = element.getAttribute( 'data-detail-link' ),
            headline = element.getAttribute( 'data-headline' ),
            refreshSeconds = element.getAttribute( 'data-refresh-seconds' ),
            showRunningGameTime = element.getAttribute( 'data-show-running-time' ),
            webSocketURL = element.getAttribute( 'data-websocket-url' ),
            wsenabled = element.getAttribute( 'data-wsenabled' );

        defaults.dataURL = backendURL || defaults.dataURL;
        defaults.detailLink = detailLink || defaults.detailLink;
        defaults.headline = headline || defaults.headline;
        defaults.refreshSeconds = parseInt( refreshSeconds ) > 0 ? parseInt( refreshSeconds ) : defaults.refreshSeconds;
        defaults.showRunningGameTime = showRunningGameTime ? showRunningGameTime.toLowerCase() === 'true' : defaults.showRunningGameTime;
        defaults.wsEnabled = wsenabled ? wsenabled.toLowerCase() === 'true' : defaults.wsEnabled;
        defaults.webSocketURL = webSocketURL || defaults.webSocketURL;
    };


    /**
     * Map supplied country codes (two and three letters)
     * in order to load svg flags
     * @param  {string}  away country code from API Call
     * @param  {string}  home country code from API Call
     * @return {array} first item is the away country, second the home country
     */
    WmTicker.prototype.mapCountryCodes = function( away, home ) {
        var countries = [{
            short: '',
            long: ''
        },
        {
            short: '',
            long: ''
        }
        ];

        for ( var i = 0; i < defaults.countries.length; i++ ) {
            var defaultsValue = defaults.countries[ i ].name.toUpperCase();
            away = away.trim().toUpperCase();
            home = home.trim().toUpperCase();
            if (  defaultsValue === away ) {
                countries[ 0 ].short = defaults.countries[ i ].short;
                countries[ 0 ].long = defaults.countries[ i ].long;
            }
            if ( defaultsValue === home ) {
                countries[ 1 ].short = defaults.countries[ i ].short;
                countries[ 1 ].long = defaults.countries[ i ].long;
            }
        }
        return countries;
    };


    /**
     * Get Difference between hours in Minutes
     * between current date and some date
     * @param  {string | Date }  date that shall be compared
     * @return {integer} negative if game is in past!
     */
    function getMinuteDifference( date ) {
        var difference = new Date() - new Date( date );
        return Math.ceil( difference / 1000 / 60 );
    }


    /**
     * Map Data from API to needed format to use in further code
     * @param  {object}  data from Kickerticker Backend
     * @return {object}
     */
    WmTicker.prototype.mapData = function( data ) {
        var returnData = {
            current: [],
            upcoming: [],
            finished: []
        };

        data.forEach( function( game ) {
            var teams = this.mapCountryCodes( game.away_name, game.home_name );
            var time = timeString( game.date, game.kickoff, game.period, game.status );
            var minutesTillGameBegins = ( new Date( game.date ) - new Date() ) / 1000;
            var preGame = minutesTillGameBegins < 3600 && game.status === 'PRE-MATCH';
            var gameShallBeBig = preGame || game.running;
            // only one game. Which shall then be displayed big
            if ( data.length === 1 ) {
                gameShallBeBig = true;
                time = ( game.status === 'FULL' ) ? 'beendet' : time; // single game big and finished shall write 'beendet'
            }

            var gameData = {
                id: game.id,
                home: game.home_name,
                homeShort: teams[ 1 ].short,
                homeLong: teams[ 1 ].long,
                homePoints: game.home_score || '-',
                away: game.away_name,
                awayShort: teams[ 0 ].short,
                awayLong: teams[ 0 ].long,
                awayPoints: game.away_score || '-',
                period: game.period,
                time: time,
                kickoff: game.kickoff,
                status: game.status,
                running: game.running,
                link: defaults.detailLink ? defaults.detailLink + game.id  : '',
                noLink: !defaults.detailLink,
                matchFinishedModifier: ( game.status === 'FULL' ) ? 'wm-ticker__match--finished' : '',
                scoreFinishedModifier: ( game.status === 'FULL' ) ? 'wm-ticker__match-score--finished' : ''
            };

            if ( game.running || gameShallBeBig ) {
                if ( game.running ) {
                    gameData.awayPoints = gameData.awayPoints > 0 ? gameData.awayPoints : '0';
                    gameData.homePoints = gameData.homePoints > 0 ? gameData.homePoints : '0';
                }
                returnData.current.push( gameData );
            } else if ( game.status === 'FULL' ) {
                returnData.finished.push( gameData );
            } else {
                returnData.upcoming.push( gameData );
            }
        }.bind( this ) );

        return {
            matches: returnData.current,
            list: returnData.finished.concat( returnData.upcoming )
        };
    };


    /**
     * get Team Points as String
     * @param  {string | integer | null}  points
     * @return {string}
     */
    WmTicker.prototype.generatePointsString = function( points ) {
        if ( points === null ) {
            return '-';
        }
        return points;
    };

    /**
     * generate time String containing all needed words
     * @param  {string}  date string supplied by API
     * @return {string}
     */
    function timeString( date, kickoff, period, status ) {
        var minuteDifference = getMinuteDifference( kickoff ),
            begin = new Date( date ),
            minutes = ( begin.getMinutes() < 10 ? '0' : '' ) + begin.getMinutes(),
            returnString = 'um ' + begin.getHours() + ':' + minutes;

        kickoff = new Date( kickoff );

        if ( defaults.showRunningGameTime ) {
            switch ( status ) {
                case 'LIVE':
                    var offsetArray = [ 0, 45, 90, 105, 120 ];
                    var cutoff = offsetArray[ period ];
                    var min = minuteDifference + offsetArray[ period - 1 ];
                    if ( min > cutoff ) {
                        returnString = cutoff + '. + ' + ( min - cutoff );
                    } else {
                        returnString = min + '.';
                    }
                    break;
                case 'HALF-TIME':
                    returnString = 'Halbzeit';
                    break;
                case 'HALF-EXTRATIME':
                    returnString = 'Halbzeit Verlängerung';
                    break;
                case 'PENALTY-SHOOTOUT':
                    returnString = 'Elfmeterschießen';
                    break;
                case 'FULL':
                    returnString = '';
                    break;
                default:
                    break;
            }
        } else {
            switch ( status ) {
                case 'PRE-MATCH':
                    returnString = 'um ' + begin.getHours() + ':' + minutes;
                    break;
                default:
                    break;
            }
        }
        return returnString;
    }

    /**
     * Count ticker time up and update view
     */
    WmTicker.prototype.updateTime = function() {
        this.data.forEach( function( game ) {
            var elem = document.getElementById( 'time-' + game.id );
            if ( elem ) {
                elem.innerText = timeString( game.date, game.kickoff, game.period, game.status );
            }
        });
    };

    /**
     * EventListener to add to overview button shown on mobile devices
     * @param  {event}  triggered event
     * @return {string}
     */
    WmTicker.prototype.showOverview = function( event ) {
        element.querySelector( '.wm-ticker__list' ).classList.remove( 'wm-ticker__list--hidden' );
        element.querySelector( '.wm-ticker__button' ).classList.add( 'wm-ticker__button--hidden' );
        event.target.removeEventListener( 'click', this.showOverview, false );
    };

    /**
     * add CSS Classes to Overview / Aside wrapper (help align css grid)
     */
    WmTicker.prototype.addGridClasses = function( listMatches ) {
        var currentGames = element.getElementsByClassName( 'wm-ticker__match-detail' );

        // no running / coming soon game
        if ( currentGames.length === 0 && listMatches.length <= 4 ) {
            element.querySelector( '.wm-ticker__list-content' ).classList.add( 'wm-ticker__list-content--grid' );

            // Add Items length as class to match css grid
            if ( listMatches.length > 0 ) {
                element.querySelector( '.wm-ticker__list-content' )
                    .classList.add( 'wm-ticker__list-content--items-' + listMatches.length );
            }
        }
    };

    /**
     * fallback for when WebSockets are not working (THIS IS AN INTERVAL!!)
     */
    WmTicker.prototype.addFallbackInterval = function() {
        // add interval to update regularly
        setInterval( this.fetchData.bind( this ), defaults.refreshSeconds * 1000 );
    };

    /**
     * fetch data via XMLHttpRequest
     */
    WmTicker.prototype.fetchData = function() {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if ( xhr.readyState === 4 && xhr.status === 200 ) {
                var data = JSON.parse( xhr.responseText );
                if ( JSON.stringify( this.data ) === JSON.stringify( data ) ) {
                    return;
                }
                this.data = data;
                this.renderView();
            }
        }.bind( this );
        xhr.open( 'GET', defaults.dataURL + defaults.dataPath, true );
        xhr.send();
    };

    /**
     * WebSocket receiving message is handled here..
     * @param  {object}  event with only updated data set. Map by Id!
     */
    WmTicker.prototype.handleWebSocketMessage = function( event ) {
        var receivedData = JSON.parse( event.data );
        var data = this.data; // work with reference to this.data

        // do not iterate over list data. That should be useless. Only large games needed
        // iterate over old data. Update if needed.
        for ( var i = 0, len = data.length; i < len; i++ ) {
            if ( data[ i ].id === receivedData.id ) {
                data[ i ].status = receivedData.status;
                data[ i ].period = receivedData.period;
                data[ i ].kickoff = receivedData.kickoff;
                data[ i ].home_score = receivedData.home_score; // eslint-disable-line camelcase
                data[ i ].away_score = receivedData.away_score; // eslint-disable-line camelcase

                // TODO: the backend should send this...
                data[ i ].running = ( receivedData.status === 'LIVE' ||
                    receivedData.status === 'HALF-TIME' ||
                    receivedData.status === 'HALF-EXTRATIME' ||
                    receivedData.status === 'PENALTY-SHOOTOUT' );

                this.renderView();
                break;
            }
        }
    };

    /**
     * what shall happen when websocket connection has ERROR is described here
     */
    WmTicker.prototype.handleWebSocketError = function() {
        this.addFallbackInterval();
    };

    /**
     * WebSocket Init
     */
    WmTicker.prototype.initWebSocket = function() {
        var ws = new WebSocket( defaults.webSocketURL + defaults.webSocketPath );

        ws.onmessage = this.handleWebSocketMessage.bind( this );
        ws.onerror = this.handleWebSocketError.bind( this );
    };

    WmTicker.prototype.renderView = function() {
        var data = this.mapData( this.data );
        var singleGame = ( data.matches.length + data.list.length ) === 1;
        var todaysGames = data.matches.length + data.list.length;

        if ( todaysGames > 0 ) {
            var template = require( 'web.core/templates/wmTicker.html' );
            template = template({
                headline: defaults.headline,
                detailLink: defaults.detailLink,
                matches: data.matches,
                matchesModifier: ( data.matches.length > 1 ) ? 'wm-ticker__match-detail--multi' : '',
                list: data.list,
                listIterator: singleGame ? [] : [ '' ] // fake iterator
            });

            // parse content to DOM
            element.innerHTML = template;

            // add show overview button on mobile if no large game available
            var button = element.querySelector( '.wm-ticker__button' );
            if ( element.querySelector( '.wm-ticker__match-detail' ) ) {
                if ( button ) {
                    button.addEventListener( 'click', this.showOverview );
                }
            } else {
                element.querySelector( '.wm-ticker__list' ).classList.remove( 'wm-ticker__list--hidden' );
                button.classList.add( 'wm-ticker__button--hidden' );
            }

            // CSS grid Hack: Add class to wrapper with the amount of children
            this.addGridClasses( data.list );
        }
    };

    new WmTicker();
}

module.exports = wmTicker;
