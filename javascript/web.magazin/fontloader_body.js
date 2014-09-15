/**
 * @fileOverview Module Fontloader
 * @version  0.1
 */
/**
 * fontloader_body.js: module for fonts
 * @module fontloader_body
 */
define(['jquery'], function($) {
    var fl = window.FontLoader;

    /**
     * fontloader_body.js: fetch font data asynchronously from the server and store it in local storage
     * @function fetchCSS
     * @param  {object} pack
     */
    var fetchCSS = function(pack) {
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

    /**
     * fontloader_body.js: initialize
     * @function init
     */
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
