/**
 * @fileOverview Module for displaying brightcove video
 * @version  0.1
 */
/**
 * Module for displaying brightcove video
 * @module displayVideo
 */
define([ 'jquery' ],
    function( $ ) {
        return {
            /**
             * Replaces a given list of dom nodes with video or return video html code
             * @function displayVideo
             * @param {string} videoId id of the video to show
             * @param {object} config configuration object
             */
            displayVideo: function( videoId, config ) {
                /**
                 * configuration object, extends config
                 * @type {object}
                 * @property {array} elem list of dom nodes to replace by video
                 * @property {object} playerData standard data about the bc player
                 * @property {object} players save require config here
                 * @property {string} html5 use 'html5' player (not available yet) or 'iframe'
                 */
                var defaults = $.extend({
                        elem: [],
                        playerData: {
                            'accountId': '18140073001',
                            'playerId': '65fa926a-0fe0-4031-8cbf-9db35cecf64a',
                            'embed': 'default'
                        },
                        players: {},
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
                        html5:  '<div class="video-player">' +
                                '<video id="player-{{videoId}}" data-account="{{accountId}}" ' +
                                'data-player="{{playerId}}" data-embed="{{embed}}" data-video-id="{{videoId}}" ' +
                                'class="video-js video-player__videotag" preload="none"></video></div>'
                    },
                    snippet,
                    scriptSrc = '//players.brightcove.net/{{accountId}}/{{playerId}}_{{embed}}/index.min';
                if ( typeof videoId === 'undefined' && defaults.elem.length < 1 ) {
                    return;
                } else {
                    snippet = templates[defaults.type]
                            .replace( /\{{accountId}}/g, defaults.playerData.accountId )
                            .replace( /\{{playerId}}/g, defaults.playerData.playerId )
                            .replace( /\{{videoId}}/g, videoId )
                            .replace( /\{{embed}}/g, 'default' );
                    $.each( defaults.elem, function( index, value ) {
                        $( defaults.elem[index] ).empty().html( snippet );
                    });
                    // in case of html5 player we have to load a script from brightcove
                    // if your site uses require.js, this same script needs to be required
                    // but for each player individually, so we need n local requires
                    if ( defaults.type === 'html5' ) {
                        // build video and account dependet js source address
                        scriptSrc = scriptSrc
                            .replace( /\{{accountId}}/g, defaults.playerData.accountId )
                            .replace( /\{{playerId}}/g, defaults.playerData.playerId )
                            .replace( /\{{embed}}/g, 'default' );
                        // add encapsuled require config per videoId
                        // http://requirejs.org/docs/api.html#multiversion
                        defaults.players[ videoId ] = require.config({
                            'paths': { 'bc': scriptSrc },
                            'timeout': 30,
                            'context': videoId
                        });
                        // require the script
                        defaults.players[ videoId ]( [ 'require', 'bc' ] );
                    }
                    return defaults.elem;
                }
            }
        };
    }
);
