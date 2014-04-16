/* global console, define */
define(function() {

    var Errors = {
        init: function() {
            var oldErrorHandler = window.onerror;
            window.jsErrors = [];

            window.onerror = function (errorMessage, url, lineNumber) {
                var link = document.createElement('a');
                link.href = url;

                var message = errorMessage + ' in ' + link.pathname + ' (line ' + lineNumber + ') @ ' + window.location.pathname;
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
