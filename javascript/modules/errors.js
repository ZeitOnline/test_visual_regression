/* global console, define */
define(function() {

    var Errors = {
        init: function() {
            var oldErrorHandler = window.onerror;
            window.jsErrors = [];

            window.onerror = function (errorMessage, url, lineNumber) {
                var message = errorMessage + ' in ' + url + ' (line ' + lineNumber + ')';
                window.jsErrors.push(message);

                if (oldErrorHandler) {
                    return oldErrorHandler(errorMessage, url, lineNumber);
                }

                return false;
            };
        }
    };

    return Errors;

});
