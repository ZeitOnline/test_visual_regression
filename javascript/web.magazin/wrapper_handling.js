/* global unescape */

/**
 * @fileOverview Module for handling of zmo navi within webview wrapper
 * @version  0.1
 */
/**
 * wrapper_handling.js: module for main navigation
 * @module wrapper_handling
 */
define(['jquery'], function() {

    /**
     * wrapper_handling.js: initialize wrapper handlers
     * @function init
     */
    var init = function() {

        /**
         * wrapper_handling.js: reads cookie
         * copied from sevenval
         * @function getCookie
        */
        function getCookie( c_name ) {
          var c_value = document.cookie;
          var c_start = c_value.indexOf(' ' + c_name + '=');

          if ( c_start === -1 ) {
            c_start = c_value.indexOf(c_name + '=');
          }
          if ( c_start === -1 ) {
            c_value = null;
          } else {
            c_start = c_value.indexOf( '=', c_start ) + 1;
            var c_end = c_value.indexOf( ';', c_start );
            if ( c_end === -1 ) {
              c_end = c_value.length;
            }
            c_value = unescape( c_value.substring( c_start,c_end ));
          }
          return c_value;
        }

        // build wrapper object which will be called from within webview
        // most of the functions here are provided by sevenval
        // as the wrapper app will call them with the wrapper namespace
        // be very careful with renaming, function names have to stick like this
        var wrapper = {
            /**
             * wrapper_handling.js: provides Ressort
             * copied from sevenval
             * @function getRessort
             */
            getRessort: function() {
                return  'Zeit Magazin';
            },
            /**
             * wrapper_handling.js: hide navigation header
             * @function hideZMOHeader
             */
            hideZMOHeader: function(){
                $( '.main-nav' ).hide();
            },
            /**
             * wrapper_handling.js: add placeholder header
             * @function setHeaderMargin
             */
            setHeaderMargin: function( _density_independant_pixels ) {
                // hide zmo navi header
                this.hideZMOHeader();

                // default: no cookie present and no change requested
                var hm = 0;

                // user has already set header margin
                if (getCookie( 'zeitwrapper_hm' )) {
                  hm = getCookie( 'zeitwrapper_hm' );
                }

                // user requested a change header margin
                if (_density_independant_pixels !== null && typeof(_density_independant_pixels) !== 'object' ) {
                  hm = _density_independant_pixels;
                }

                // set and save settings if in valid scope
                $( '.main-nav' ).before( '<header id="wrapper_spacer_header"></header>' );
                $( '#wrapper_spacer_header' ).attr( 'style', 'height:' + hm + 'px');
                document.cookie = 'zeitwrapper_hm=' + hm +'; expires=Thu, 31 Dec 2099 23:59:59 UTC; path=/';
            }
        };

    };

    return {
        init: init
    };

});
