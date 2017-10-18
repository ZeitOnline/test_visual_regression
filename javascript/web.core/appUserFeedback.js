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

    var response = {};

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
            this.init();
        }
    }

    // get json
    var path = window.location.protocol + '//' + window.location.host + '/json/appUserFeedback' + mobileConf + '.json';

    AppUserFeedback.prototype.getData = function( url ) {
        // Promises working since iOS Safari8, Android Browser 4.4.4
        return new window.Promise( function( resolve, reject ) {
            var xhr = new XMLHttpRequest();
            xhr.open( 'GET', url );
            xhr.onload = function() {
                // This is called even on 404 etc
                // so check the status
                if ( xhr.status === 200 ) {
                    // Resolve the promise with the settings text
                    resolve( JSON.parse( xhr.response ) );
                } else {
                    // Otherwise reject with the status text
                    // which will hopefully be a meaningful error
                    reject( Error( xhr.statusText ) );
                }
            };
            // Handle network errors
            xhr.onerror = function() {
                reject( Error( 'Network Error' ) );
            };
            // Make the request
            xhr.send();
        });
    };

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
        for ( var i = 0; i < response.questions.length; i++ ) {
            var html = template({
                question: response.questions[ i ].question,
                antwortPos: response.questions[ i ].antwortPos,
                linkYes: response.questions[ i ].linkPos,
                antwortNeg: response.questions[ i ].antwortNeg,
                linkNo: response.questions[ i ].linkNeg,
                identifier: response.questions[ i ].identifier,
                visibility: response.questions[ i ].visibility
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
                        window.location = response.link1Yes;
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
                        window.location = response.link1No;
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
        for ( buttons = 0; buttons < response.questions.length; buttons++ ) {
            funcs[ buttons ] = generateButton({
                linkYes: response.questions[ buttons ].linkPos,
                linkNo: response.questions[ buttons ].linkNeg,
                identifier: response.questions[ buttons ].identifier,
                visibility: response.questions[ buttons ].visibility
            });
        }

        for ( j = 0; j < response.questions.length; j++ ) {
            funcs[ j ]();
        }
    };

    AppUserFeedback.prototype.init = function() {
        this.getData( path ).then( function( response ) {
            console.log( response.questions );
            if ( response ) {
                this.showQuestions();
            }
        });
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
