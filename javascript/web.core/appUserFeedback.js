/**
 * @fileOverview function for a feedback notification
 * @version  0.1
 * @author  jan-paul.bauer@zeit.de
 */

function appUserFeedback() {
    'use strict';

    /**
     * setup options or defaults
     */

    /**
     * default options
     * @property {string} link          link* can use as external (http//) or internal (quest1 etc.) or for closing feedback (close)
    */

    var defaults = {
        quest1: 'Gefällt Ihnen die ZEIT ONLINE App?',
        answ1Yes: 'ja',
        link1Yes: 'quest2',
        answ1No: 'nein',
        link1No: 'close',
        quest2: 'Wollen Sie die App bewerten?',
        answ2Yes: 'ja',
        link2Yes: 'quest1',
        answ2No: 'nein, danke',
        link2No: 'quest3',
        quest3: 'Wollen Sie uns Feedback geben?',
        answ3Yes: 'ja',
        link3Yes: 'http://www.zeit.de/feedback',
        answ3No: 'nein',
        link3No: 'close'
    };

    // check mobile devices and pick config
    var userAgent = navigator.userAgent || navigator.vendor || window.opera;
    var mobileConf = 'Default';

    if ( /android/i.test( userAgent ) ) {
        mobileConf = 'Android';
    } else if ( /iPad|iPhone|iPod/.test( userAgent ) && !window.MSStream ) {
        mobileConf = 'Apple';
    } else {
        mobileConf = 'Default';
    }

    // get json
    var options = require( 'web.core/templates/appUserFeedback' + mobileConf + '.json' );

    var extend = function( defaults, options ) {
    // merge defaults with user options
        var extended = {};
        var prop;
        for ( prop in defaults ) {
            if ( Object.prototype.hasOwnProperty.call( defaults, prop ) ) {
                extended[ prop ] = defaults[ prop ];
            }
        }
        for ( prop in options ) {
            if ( Object.prototype.hasOwnProperty.call( options, prop ) ) {
                extended[ prop ] = options[ prop ];
            }
        }
        return extended;
    };

    /**
     * check cookie and initial functions
     */
    function AppUserFeedback() {
        if ( document.cookie.indexOf( 'zeit_app_feedback' ) === -1 ) {
            this.showQuestions();
            this.next();
        }
    }

    // settings (defaults || options)
    var settings = extend( defaults, options );

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
     * show rendered mustache template
     */
    AppUserFeedback.prototype.showQuestions = function() {
        // mustache template-data
        var template = require( 'web.core/templates/appUserFeedback.html' ),
            html = template({
                frage1: settings.quest1,
                antwort1Pos: settings.answ1Yes,
                link1Yes: settings.link1Yes,
                antwort1Neg: settings.answ1No,
                link1No: settings.link1No,
                frage2: settings.quest2,
                antwort2Pos: settings.answ2Yes,
                link2Yes: settings.link2Yes,
                antwort2Neg: settings.answ2No,
                link2No: settings.link2No,
                frage3: settings.quest3,
                antwort3Pos: settings.answ3Yes,
                link3Yes: settings.link3Yes,
                antwort3Neg: settings.answ3No,
                link3No: settings.link3No
            });

        // add template to source code
        var siteElement = document.querySelector( '.article-page' );
        siteElement.insertAdjacentHTML( 'afterend', html );
    };

    /**
     * track, show and hide questions
     */
    AppUserFeedback.prototype.next = function() {
        // feedbackform
        var divFeedback = document.getElementById( 'app-user-feedback' );

        // buttons
        var buttonYes1 = document.getElementById( 'anws1yes' );
        var buttonNo1 = document.getElementById( 'anws1no' );
        var buttonYes2 = document.getElementById( 'anws2yes' );
        var buttonNo2 = document.getElementById( 'anws2no' );
        var buttonYes3 = document.getElementById( 'anws3yes' );
        var buttonNo3 = document.getElementById( 'anws3no' );

        // questions
        var questDiv1 = document.getElementById( 'quest1' );
        var questDiv2 = document.getElementById( 'quest2' );
        var questDiv3 = document.getElementById( 'quest3' );

        // question 1
        if ( buttonYes1 ) {
            buttonYes1.addEventListener( 'touchstart', function() {
                if ( !settings.link1Yes.indexOf( 'http' ) ) {
                    window.location = settings.link1Yes;
                } else {
                    questDiv1.style.display = 'none';
                    document.getElementById( settings.link1Yes ).style.display = 'block';
                }
            }, false );
        }

        if ( buttonNo1 ) {
            buttonNo1.addEventListener( 'touchstart', function() {
                if ( !settings.link1No.indexOf( 'http' ) ) {
                    window.location = settings.link1No;
                } else if ( !settings.link1No.indexOf( 'close' ) ) {
                    divFeedback.style.display = 'none';
                    AppUserFeedback.prototype.showTime();
                } else {
                    questDiv1.style.display = 'none';
                    document.getElementById( settings.link1No ).style.display = 'block';
                }
            }, false );
        }

        // question 2
        if ( buttonYes2 ) {
            buttonYes2.addEventListener( 'touchstart', function() {
                if ( !settings.link2Yes.indexOf( 'http' ) ) {
                    window.location = settings.link2Yes;
                } else {
                    questDiv2.style.display = 'none';
                    document.getElementById( settings.link2Yes ).style.display = 'block';
                }
            }, false );
        }

        if ( buttonNo2 ) {
            buttonNo2.addEventListener( 'touchstart', function() {
                if ( !settings.link2No.indexOf( 'http' ) ) {
                    window.location = settings.link2No;
                } else if ( !settings.link2No.indexOf( 'close' ) ) {
                    divFeedback.style.display = 'none';
                    AppUserFeedback.prototype.showTime();
                } else {
                    questDiv2.style.display = 'none';
                    document.getElementById( settings.link2No ).style.display = 'block';
                }
            }, false );
        }

        // question 3
        if ( buttonYes3 ) {
            buttonYes3.addEventListener( 'touchstart', function() {
                if ( !settings.link3Yes.indexOf( 'http' ) ) {
                    window.location = settings.link3Yes;
                } else {
                    questDiv3.style.display = 'none';
                    document.getElementById( settings.link3Yes ).style.display = 'block';
                }
            }, false );
        }

        if ( buttonNo3 ) {
            buttonNo3.addEventListener( 'touchstart', function() {
                if ( !settings.link3No.indexOf( 'http' ) ) {
                    window.location = settings.link3No;
                } else if ( !settings.link3No.indexOf( 'close' ) ) {
                    divFeedback.style.display = 'none';
                    AppUserFeedback.prototype.showTime();
                } else {
                    questDiv3.style.display = 'none';
                    document.getElementById( settings.link3No ).style.display = 'block';
                }
            }, false );
        }
    };

    // just start the app once
    if ( document.querySelector( '#app-user-feedback' ) ) {
        return;
    } else {
        new AppUserFeedback();
    }
}

module.exports = appUserFeedback;
