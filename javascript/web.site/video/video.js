/**
 * @fileOverview Module for displaying brightcove video
 * @version  0.1
 */

var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' );

/**
 * Module for displaying brightcove video
 * @module video
 */
var video = {
    scripts: {},

    /**
     * Replaces a given list of dom nodes with video
     * @function displayVideo
     * @param {string} videoId id of the video to show
     * @param {object} config configuration object
     */
    displayVideo: function( videoId, config ) {

        var advertising = ( zeit.cookieRead( 'gdpr' ) === 'dnt' ) ?
                'withoutAds' : config.advertising,
            videoPlayerId = zeit.videoPlayers[ config.playertype ][ advertising ];

        /**
         * configuration object, extends config
         * @type {object}
         * @property {object} elem jQuery collection to replace by video
         * @property {object} playerData standard data about the bc player
         */
        var defaults = $.extend({
                elem: [],
                playerData: {
                    'accountId': '18140073001',
                    'playerId': videoPlayerId,
                    'embed': 'default'
                }
            }, config ),

            /**
             * html template for player code
             */
            template = '<div class="video-player">' +
                        '<video id="player-{{videoId}}" data-account="{{accountId}}" ' +
                        'data-player="{{playerId}}" data-embed="{{embed}}" data-video-id="{{videoId}}" ' +
                        'class="video-js video-player__videotag" preload="none" controls playsinline></video></div>',
            snippet,
            scriptSrc = 'https://players.brightcove.net/{{accountId}}/{{playerId}}_{{embed}}/index.min.js';

        if ( typeof videoId === 'undefined' && defaults.elem.length < 1 ) {
            return;
        }

        snippet = template
            .replace( /\{{accountId}}/g, defaults.playerData.accountId )
            .replace( /\{{playerId}}/g, defaults.playerData.playerId )
            .replace( /\{{videoId}}/g, videoId )
            .replace( /\{{embed}}/g, 'default' );

        defaults.elem.empty().html( snippet );

        // if your site uses require.js, this same script needs to be required
        // but for each player individually, so we need n local requires

        // build video and account dependent script source address
        scriptSrc = scriptSrc
            .replace( /\{{accountId}}/g, defaults.playerData.accountId )
            .replace( /\{{playerId}}/g, defaults.playerData.playerId )
            .replace( /\{{embed}}/g, 'default' );

        // skip loading if script already added
        if ( this.scripts[ scriptSrc ]) {
            return;
        }

        // add script with callback
        var script = document.createElement( 'script' ),
            done = false;

        this.scripts[ scriptSrc ] = true;
        script.src = scriptSrc;
        script.onload = script.onreadystatechange = function() {
            if ( !done && ( !this.readyState || this.readyState === 'loaded' || this.readyState === 'complete' ) ) {
                done = true;

                // We have to take care of the brightcove plaver if loaded as AMD
                // https://support.brightcove.com/requirejs-and-brightcove-player
                // brighcove checks for global define to recognize RequireJS
                // This is ill. It will break the internet.
                if ( typeof window.bc !== 'function' && typeof window.define === 'function' && window.define.amd ) {
                    // add encapsuled require config per videoId
                    // http://requirejs.org/docs/api.html#multiversion
                    var rjs = window.require.config({
                        'paths': { 'bc': scriptSrc },
                        'timeout': 30,
                        'context': videoId
                    });
                    // require the script
                    rjs([ 'require', 'bc' ]);
                }

                script.onload = script.onreadystatechange = null;
            }
        };

        document.body.appendChild( script );
    }

};

module.exports = video;
