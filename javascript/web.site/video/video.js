/**
 * @fileOverview Module for displaying brightcove video
 * @version  0.1
 */
/**
 * Module for displaying brightcove video
 * @module video
 */
var video = {
    init: function() {
        var $ = require( 'jquery' );

        return {

            /**
             * Replaces a given list of dom nodes with video
             * @function displayVideo
             * @param {string} videoId id of the video to show
             * @param {object} config configuration object
             */
            displayVideo: function( videoId, config ) {

                /**
                 * configuration object, extends config
                 * @type {object}
                 * @property {object} elem jQuery collection to replace by video
                 * @property {object} playerData standard data about the bc player
                 * @property {string} type use 'html5' player or 'iframe'
                 */
                var defaults = $.extend({
                        elem: [],
                        playerData: {
                            'accountId': '18140073001',
                            'playerId': window.Zeit.cpVideoPlayerId,
                            'embed': 'default'
                        },
                        type: 'html5'
                    }, config ),

                    /**
                     * html templates for player code
                     * @type {Object}
                     * @property {string} iframe code for the iframe player
                     * @property {string} html5 code for the html5 player
                     */
                    templates = {
                        iframe: '<div class="video-player">' +
                                '<iframe class="video-player__iframe" ' +
                                'src="//players.brightcove.net/{{accountId}}/' +
                                '{{playerId}}_default/index.html?videoId={{videoId}}" ' +
                                'allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe></div>',
                        html5: '<div class="video-player">' +
                                '<video id="player-{{videoId}}" data-account="{{accountId}}" ' +
                                'data-player="{{playerId}}" data-embed="{{embed}}" data-video-id="{{videoId}}" ' +
                                'class="video-js video-player__videotag" preload="none" controls></video></div>'
                    },
                    snippet,
                    scriptSrc = window.location.protocol + '//players.brightcove.net/{{accountId}}/{{playerId}}_{{embed}}/index.min.js';
                if ( typeof videoId === 'undefined' && defaults.elem.length < 1 ) {
                    return;
                } else {
                    snippet = templates[ defaults.type ]
                        .replace( /\{{accountId}}/g, defaults.playerData.accountId )
                        .replace( /\{{playerId}}/g, defaults.playerData.playerId )
                        .replace( /\{{videoId}}/g, videoId )
                        .replace( /\{{embed}}/g, 'default' );

                    defaults.elem.empty().html( snippet );

                    // in case of html5 player we have to load a script from brightcove
                    // if your site uses require.js, this same script needs to be required
                    // but for each player individually, so we need n local requires
                    if ( defaults.type === 'html5' ) {
                        // build video and account dependent script source address
                        scriptSrc = scriptSrc
                            .replace( /\{{accountId}}/g, defaults.playerData.accountId )
                            .replace( /\{{playerId}}/g, defaults.playerData.playerId )
                            .replace( /\{{embed}}/g, 'default' );

                        // add script with callback to create a player instance and play the video
                        var script = document.createElement( 'script' ),
                            _define = window.define, // be nice, keep a reference
                            done = false;

                        // prevent clash of brightcove script with third party scripts using require.
                        // brighcove checks for global define to recognize RequireJS
                        // This is ill. It will break the internet.
                        window.define = undefined;

                        script.src = scriptSrc;
                        script.onload = script.onreadystatechange = function() {
                            if ( !done && ( !this.readyState || this.readyState === 'loaded' || this.readyState === 'complete' ) ) {
                                done = true;
                                /*global videojs*/
                                videojs( 'player-' + videoId ).play();
                                window.define = _define; // reset previous state
                                script.onload = script.onreadystatechange = null;
                            }
                        };
                        document.body.appendChild( script );
                    }

                    return defaults.elem;
                }
            }
        };
    }
};

module.exports = video.init();
