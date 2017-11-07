/**
 * @fileOverview Track visibility of elements to webtrekk
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
/**
 * Version 0.1 only serves one purpose: tracking the visibility of the "gate"
 * on paywalled articles to webtrekk. Visibility means: this thing is in
 * the users viewport. As soon as we want to track more elements, we need
 * to add some abstraction and initialize every element->tracking
 * configuration from outside or from a config object or something.
 * Hint: We could even use one IntersectionObserver for different actions,
 * but need to coordinate triggers and handlers.
 */
define([ 'web.core/clicktracking' ], function( Clicktracking ) {

    var observer;

    var handleIntersectionEvent = function( targets ) {
        // we only have one element for now, and do not have to iterate over them
        if ( targets[ 0 ].isIntersecting ) {
            Clicktracking.send([ 'article.schranke...view', '#schranke-' + window.Zeit.view.paywall ]);
            observer.disconnect();
            // müssen/können wir jetzt das ganze Modul wegschmeißen?
        }
    };

    var init = function() {

        // Checks via https://github.com/w3c/IntersectionObserver/tree/gh-pages/polyfill
        // Exits early if all IntersectionObserver and IntersectionObserverEntry
        // features are natively supported.
        if ( 'IntersectionObserver' in window &&
            'IntersectionObserverEntry' in window &&
            'intersectionRatio' in window.IntersectionObserverEntry.prototype ) {

            // Minimal polyfill for Edge 15's lack of `isIntersecting`
            // See: https://github.com/w3c/IntersectionObserver/issues/211
            if ( !( 'isIntersecting' in window.IntersectionObserverEntry.prototype ) ) {
                Object.defineProperty( window.IntersectionObserverEntry.prototype,
                    'isIntersecting', {
                        get: function() {
                            return this.intersectionRatio > 0;
                        }
                    });
            }

            observer = new window.IntersectionObserver(
                handleIntersectionEvent,
                { threshold: 0.5 }
            );
            observer.observe( document.querySelector( '.gate' ) );

        }
    };

    return {
        init: init
    };
});
