/* global console, define, alert, sjcl */

define(['jquery'], function() {

    var init = function() {
        // sjcl can now be used here...
        sjcl.encrypt("password", "data");
    };

    return {
        init: init
    };

});
