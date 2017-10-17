/**
 * @fileOverview function for a feedback notification
 * @version  0.1
 * @author  jan-paul.bauer@zeit.de
 */

function appUserFeedback() {
    'use strict';

    /**
     * setup options
     */

    // check mobile devices and pick config
    var userAgent = navigator.userAgent || navigator.vendor || window.opera;
    var mobileConf = 'Default';

    if ( /android/i.test( userAgent ) ) {
        mobileConf = 'Android';
    } else if ( /iPad|iPhone|iPod/.test( userAgent ) && !window.MSStream ) {
        mobileConf = 'Apple';
    }

    /**
     * check cookie and initial functions
     */
    function AppUserFeedback() {
        if ( document.cookie.indexOf( 'zeit_app_feedback' ) === -1 ) {
            this.showQuestions();
        }
    }

    // get json
    //var settings = require( 'web.core/templates/appUserFeedback' + mobileConf + '.json' );

    var endpoint = window.location.protocol + '//' + window.location.host + '/json/appUserFeedback' + mobileConf + '.json';

    var jsonValues = ( function() {
        var json;
        function fetchJSONFile( endpoint, callback ) {
            var httpRequest = new XMLHttpRequest();
            httpRequest.onreadystatechange = function() {
                if ( httpRequest.readyState === 4 ) {
                    if ( httpRequest.status === 200 ) {
                        var data = JSON.parse( httpRequest.responseText );
                        if ( callback ) {
                            callback( data );
                        }
                    }
                }
            };
            httpRequest.open( 'GET', endpoint );
            httpRequest.send();
        }

        fetchJSONFile( endpoint, function( data ) {
            json = data;
        });

        return { getData: function() {
            if ( json ) {
                console.log( endpoint );
                return json;
            } else {
                console.log( endpoint );
                return false;
            }
        } };

    })();

    var settings = jsonValues.getData();

    /**
     * set cookie for expiring to show feedback after several time again
     */
    AppUserFeedback.prototype.showTime = function() {
        var now = new Date();
        var time = now.getTime();
        var expireTime = time + 31 * 86400000; // one month
        now.setTime( expireTime );
        document.cookie = 'zeit_app_feedback=1;expires=' + now.toGMTString() + ';path=/';
    };

    /**
     * count and get data from json and show rendered mustache template
     */
    AppUserFeedback.prototype.showQuestions = function() {
        // mustache template-data
        var template = require( 'web.core/templates/appUserFeedback.html' );
        var count = 0;
        for ( var i = 0; i < settings.questions.length; i++ ) {
            var html = template({
                question: settings.questions[ i ].question,
                antwortPos: settings.questions[ i ].antwortPos,
                linkYes: settings.questions[ i ].linkPos,
                antwortNeg: settings.questions[ i ].antwortNeg,
                linkNo: settings.questions[ i ].linkNeg,
                identifier: settings.questions[ i ].identifier,
                visibility: settings.questions[ i ].visibility
            });

            // add template to source code
            var siteElement = document.querySelector( '.article-page' );
            siteElement.insertAdjacentHTML( 'afterend', html );
            count++;
        }

        console.log( count + ' questions in stock.' );

        // generate touch functionality for each button
        var buttons = 0;
        var j = 0;
        var funcs = [];

        // button logic
        function generateButton( buttonID ) {
            return function() {
                // positive answer
                document.getElementById( 'anwsyes' + buttonID.identifier ).addEventListener( 'touchstart', function( event ) {
                    event.preventDefault();
                    if ( !buttonID.linkYes.indexOf( 'http' ) ) {
                        window.location = settings.link1Yes;
                        AppUserFeedback.prototype.showTime();
                    } else if ( !buttonID.linkYes.indexOf( 'close' ) ) {
                        document.getElementById( buttonID.identifier ).style.display = 'none';
                        AppUserFeedback.prototype.showTime();
                    } else {
                        document.getElementById( buttonID.identifier ).style.display = 'none';
                        document.getElementById( buttonID.linkYes ).style.display = 'block';
                    }
                }, false );

                // negative answer
                document.getElementById( 'anwsno' + buttonID.identifier ).addEventListener( 'touchstart', function( event ) {
                    event.preventDefault();
                    if ( !buttonID.linkNo.indexOf( 'http' ) ) {
                        window.location = settings.link1No;
                        AppUserFeedback.prototype.showTime();
                    } else if ( !buttonID.linkNo.indexOf( 'close' ) ) {
                        document.getElementById( buttonID.identifier ).style.display = 'none';
                        AppUserFeedback.prototype.showTime();
                    } else {
                        document.getElementById( buttonID.identifier ).style.display = 'none';
                        document.getElementById( buttonID.linkYes ).style.display = 'block';
                    }
                }, false );
            };
        }

        // iterate through needed settings
        for ( buttons = 0; buttons < settings.questions.length; buttons++ ) {
            funcs[ buttons ] = generateButton({
                linkYes: settings.questions[ buttons ].linkPos,
                linkNo: settings.questions[ buttons ].linkNeg,
                identifier: settings.questions[ buttons ].identifier,
                visibility: settings.questions[ buttons ].visibility
            });
        }

        for ( j = 0; j < settings.questions.length; j++ ) {
            funcs[ j ]();
        }
    };

    // just start the app once
    if ( document.querySelector( '.app-user-feedback' ) ) {
        return;
    } else {
        new AppUserFeedback();
        console.log( 'start feedback notification.' );
    }
}

module.exports = appUserFeedback;
