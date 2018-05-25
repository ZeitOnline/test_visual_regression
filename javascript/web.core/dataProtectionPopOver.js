/**
 * @fileOverview Script to dismiss / show data-protection popover
 * @author hennes.roemmer@zeit.de
 * @version  0.1
 */
define([
    'jquery',
    'web.core/zeit',
    'jquery.inview' ], function( $, Zeit ) {
    var defaults = {
        cookieName: 'Data-Protection-Popover-Dismissed',
        popOver: document.getElementById( 'data-protection-overlay' ),
        popOverButton: document.getElementById( 'dataProtection-popover-dismiss' ),
        inViewElement: '.footer'
    };

    function hidePopOver() {
        Zeit.cookieCreate( defaults.cookieName, 'true' );
        defaults.popOver.classList.add( 'data-protection--hidden' );
    }

    function showPopOver() {
        defaults.popOver.classList.remove( 'data-protection--hidden' );
    }

    function popOverShouldBeVisible() {
        if ( defaults.popOver.classList.length === 2 && Zeit.cookieRead( 'Data-Protection-Popover-Dismissed' ) !== 'true' ) {
            return true;
        }
        return false;
    }

    function addClickEventListenerToButton() {
        defaults.popOverButton.addEventListener( 'click', function() {
            hidePopOver();
        });
    }

    function handleFooterInView() {
        $( defaults.inViewElement ).on( 'inview', function( event, isInView ) {
            if ( isInView ) {
                defaults.popOver.classList.add( 'data-protection--hidden' );
            } else {
                defaults.popOver.classList.remove( 'data-protection--hidden' );
            }
        });
    }

    function addMobileRefreshStop() {
        var div = document.createElement( 'div' );
        div.id = '#app-user-is-back';
        document.querySelector( 'body' ).append( div );
    }

    return {
        init: function() {
            if ( document.querySelector( '#data-protection-overlay' ) ) {
                // show Popover
                if ( popOverShouldBeVisible() ) {
                    showPopOver();
                    addClickEventListenerToButton();
                    handleFooterInView();
                    addMobileRefreshStop();
                }
            }
        }
    };
});
