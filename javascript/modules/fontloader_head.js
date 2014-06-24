/* global console */

/**
 * font loader setup
 */
window.FontLoader = (function(ZMO) {
    // privates
    var prefix = 'de.zeit.zmo__webfonts--',
        suffix = '--version',
        // set up all font packages we need
        fontDictionary = [
            {
                identifier: 'base',
                selector: null,
                path: ZMO.home + 'css/standalone-fonts/base.css',
                version: "2.1"
            }
        ],
        linkTag = document.getElementsByTagName('link')[0],
        // detect modern browsers that support woff
        isModernBrowser = ('querySelector' in document) && ('localStorage' in window) && ('addEventListener' in window) && Array.prototype.forEach && (document.documentElement.className.indexOf( "lt-ie9" ) === -1);

    // module object
    var fl = {
        enabled: isModernBrowser,
        scheduledFonts: [],
        getFontKey: function(pack) {
            return prefix + pack.identifier;
        },
        getVersionKey: function(pack) {
            return prefix + pack.identifier + suffix;
        },
        lazyLoadFont: function(pack) {
            // queue font pack download for later
            this.scheduledFonts.push(pack);
        },
        appendCSS: function(style) {
            // create a style tag in the <head> filled with raw font-face declarations
            var styleTag = document.createElement('style');
            styleTag.innerHTML = style;
            if (linkTag && linkTag.parentNode) {
                linkTag.parentNode.insertBefore(styleTag, linkTag);
            }
        }
    };

    // load fonts from localstorage or queue up for lazy loading
    var init = function() {
        // run through all font packs in the dictionary
        fontDictionary.forEach(function(pack) {
            var data = localStorage.getItem(fl.getFontKey(pack)),
                version = localStorage.getItem(fl.getVersionKey(pack));

            if (data && pack.version === version) {
                // font is in localstorage, drop data in style tag immediately
                fl.appendCSS(data);
            } else {
                // font is not in localstorage or outdated, queue font download for later
                fl.lazyLoadFont(pack);
            }
        });
    };

    // only load fonts if modern browser
    if (isModernBrowser) {
        init();
    }

    return fl;
})(window.ZMO);
