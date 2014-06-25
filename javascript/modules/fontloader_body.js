/* global console, define */

define(['jquery'], function($) {
    var fl = window.FontLoader;

    var fetchCSS = function(pack) {
        // fetch font data asynchronously from the server and store it in local storage
        $.ajax({
            url: pack.path,
            success: function (data) {
                // we’ve got the fonts, store them in localstorage and apply them
                localStorage.setItem(fl.getFontKey(pack), data);
                localStorage.setItem(fl.getVersionKey(pack), pack.version);
                fl.appendCSS(data);
            }
        });
    };

    var init = function() {
        if (fl.enabled) {
            // lazy load queued fonts after document ready
            $(function() {
                fl.scheduledFonts.forEach(function(pack) {
                    // apply fonts only if no selector present or selector matches at least one element
                    if (!pack.selector || document.querySelector(pack.selector)) {
                        // get font data via ajax and store
                        fetchCSS(pack);
                    }
                });
            });
        }
    };

    return {
        init: init
    };

});
