/**
 * @fileOverview function for a feedback notification
 * @version  0.1
 * @author  jan-paul.bauer@zeit.de
 * @author  tobias.weiss@zeit.de
 */

function appUserFeedback() {
    'use strict';
    // debug flag for dev purposes
    var debug = window.location.href.indexOf( 'force-userfeedback' ) > -1;

    function AppUserFeedback() {
        var userAgent = navigator.userAgent || navigator.vendor || window.opera,
            mobileConf = 'Default',
            feedbackForm = document.querySelector( '.app-feedback' );

        if ( /android/i.test( userAgent ) ) {
            mobileConf = 'Android';
        } else if ( /iPad|iPhone|iPod/.test( userAgent ) && !window.MSStream ) {
            mobileConf = 'Apple';
        }

        // path to json config
        this.path = window.location.protocol + '//' + window.location.host + '/json/appUserFeedback' + mobileConf + '.json';

        if ( !feedbackForm ) {
            this.init();
        }
    }

    AppUserFeedback.prototype.getData = function( url ) {
        // Promises working since iOS Safari8, Android Browser 4.4.4
        return new window.Promise( function( resolve, reject ) {
            var xhr = new XMLHttpRequest(),
                errorURL;
            xhr.open( 'GET', url );
            xhr.onload = function() {
                // This is called even on 404 etc
                // so check the status
                if ( xhr.status === 200 ) {
                    // Resolve the promise with the settings text
                    resolve( JSON.parse( xhr.response ) );
                } else {
                    // Otherwise reject with the status text
                    // Eeror out meaningfully w/ request URL if possible
                    errorURL = xhr.responseURL ? ': ' +  xhr.responseURL : '';
                    reject( Error( xhr.statusText + errorURL ) );
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

    // don't bother users w/ feedback-form if they've already dealt with it
    AppUserFeedback.prototype.setCookie = function() {
        var now = new Date(),
            time = now.getTime(),
            expireTime = time + 31 * 86400000; // one month
        now.setTime( expireTime );
        document.cookie = 'zeit_app_feedback=1;expires=' + now.toGMTString() + ';path=/';
    };

    AppUserFeedback.prototype.renderView = function( config ) {
        // mustache template-data
        var template = require( 'web.core/templates/appUserFeedback.html' ),
            // for multipage view (komplettansicht), we have to select the last page
            articlePages = document.querySelectorAll( '.article-page' ),
            articleLastPage = articlePages.item( articlePages.length-1 ),
            currentConfig = !config ? this.responseObj.view_1 : this.responseObj[ config ],
            form = template({
                question: currentConfig.question,
                feedbackPositive: currentConfig.feedback_positive,
                feedbackNegative: currentConfig.feedback_negative
            });
        articleLastPage.insertAdjacentHTML( 'afterend', form );
        // expose cureent data set to instance's scope
        this.currentConfig = currentConfig;
    };

    AppUserFeedback.prototype.next = function( evt ) {
        var feedbackForm = document.querySelector( '.app-feedback' ),
            nextScreen = this.currentConfig[ 'target_' + evt.target.dataset.action ];

        // remove current view from DOM
        feedbackForm.parentNode.removeChild( feedbackForm );

        if ( nextScreen ) {
            // is nextScreen a URL?
            // it's also possible to specify a zeitapp link (e.g. zeitapp://settings)
            if ( nextScreen.indexOf( 'http' ) === 0 || nextScreen.indexOf( 'zeitapp' ) === 0 ) {
                window.location.href = nextScreen;
            // if not so, render the next view
            } else if ( nextScreen !== 'false' ) {
                this.renderView( nextScreen );
                this.addFormListener();
            }
        }
    };

    AppUserFeedback.prototype.addFormListener = function() {
        // establish common ground by proxying outer scope
        var that = this,
            formAction = document.querySelectorAll( '.app-feedback__action' );
        for ( var j = 0; j < formAction.length; j++ ) {
            formAction[ j ].addEventListener( 'click', function( e ) {
                // 'this' would return e.target here
                // js-hint is disabled, outer scoped callback assigned here on purpose
                /* jshint ignore:start */
                that.next( e );
                /* jshint ignore:end */
            });
        }
    };

    AppUserFeedback.prototype.init = function() {
        // establish common ground by proxying outer scope
        var that = this;
        that.getData( that.path ).then( function( response ) {
            that.responseObj = response;
        }).then( function() {
            that.renderView();
        }).then( function() {
            that.addFormListener();
        }).then( function() {
            that.setCookie();
        });
    };

    // instantiate just once
    if ( document.cookie.indexOf( 'zeit_app_feedback' ) === -1 || debug ) {
        new AppUserFeedback();
    }
}

module.exports = appUserFeedback;
