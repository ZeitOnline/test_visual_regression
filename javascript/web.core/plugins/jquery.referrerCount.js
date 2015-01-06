/**
* @fileOverview Zeit Online Plugin for counting multiple referrer
* @version  0.1
*
* Plugin identifies referrers and checks against a list of site we want to count
* saves user specific count into a data structure in localstorage
* and supplies API to get Counts from storage
*
* Copyright (c) 2014 ZEIT ONLINE, http://www.zeit.de
* Dual licensed under the MIT and GPL licenses:
* http://www.opensource.org/licenses/mit-license.php
* http://www.gnu.org/licenses/gpl.html
*
* @author Nico Bruenjes
*/

(function( $, win, doc ) {
    /**
    * See (http://jquery.com/)
    * @name jQuery
    * @alias $
    * @class jQuery Library
    * See the jQuery Library  (http://jquery.com/) for full details.  This just
    * documents the function and classes that are added to jQuery by this plug-in.
    */
    /**
    * See (http://jquery.com/)
    * @name fn
    * @class jQuery Library
    * See the jQuery Library  (http://jquery.com/) for full details.  This just
    * documents the function and classes that are added to jQuery by this plug-in.
    * @memberOf jQuery
    */
    /**
     * Counts and saves referrers to localstorage and returns them on question
     * @class referrerCount
     * @memberOf jQuery.fn
     * @param {string} arg methodname to call from plugin, if ommited, init is called
     * @param {*} [options…] arguments to methods
    */

    var defaults = {
            storageName: 'referrerCount',
            sites: [
                { name: 'facebook', regex: /facebook\.com/ },
                { name: 'twitter', regex: /t\.co|twitter\.com/ }
            ]
        },
        hasLocalstorage = function() {
            try {
                return ('localStorage' in win) && ('setItem' in localStorage)
            } catch(e) {
                return false;
            }
        },
        methods = {
            /**
             * checks the referrer against the list of sites
             * usage: $(window).referrerCount('getData', 'twitter'), $(window).referrerCount('getData')
             * @memberOf referrerCount
             * @category Function
             * @returns {(string|bool)} site identifier or false
            */
            checkReferrer: function() {
                // check against sites
                var ret = false;
                $.each( defaults.sites, function( i, n ) {
                    if( doc.referrer.search(n.regex) > -1 ) {
                        ret = n.name;
                        return false; // return false to exit loop
                    }
                });
                return ret;
            },
            /**
             * checks if there is and if its an external referrer
             * @memberOf referrerCount
             * @public
             * @category Function
             * @param {string} [name] name of the data field in storage, if omitted the whole data object is returned
             * @returns {(number|object)} actual count or complete data object
            */
            getData: function( name ) {
                var data = JSON.parse( localStorage.getItem( defaults.storageName ) );
                if ( typeof name !== 'undefined' ) {
                    return data !== null ? data[name] : 0;
                } else {
                    return data !== null ? data : {};
                }
            },
            /**
             * checks if there is and if its an external referrer
             * @memberOf referrerCount
             * @public
             * @category Function
             * @returns {boolean}
            */
            hasExternalReferrer: function() {
                return document.referrer && document.referrer.indexOf(location.protocol + "//" + location.host) !== 0;
            },
            /**
             * checks lookup the count for name and increment it
             * @memberOf referrerCount
             * @public
             * @category Function
             * @param {string} name name to lookup in data
            */
            incrementVisit: function( name ) {
                var data = methods.getData(),
                    value;
                if ( typeof data[ name ] !== 'undefined' ) {
                    value = parseInt( data[ name ], 10 );
                    data[ name ] = value + 1;
                } else {
                    data[ name ] = 1;
                }
                localStorage.setItem(defaults.storageName, JSON.stringify( data ) );
            },
            /**
             * checks lookup the count for name and increment it
             * @memberOf referrerCount
             * @public
             * @category Function
             * @param {object} options jQuery options object to extend
            */
            init: function( options ) {
                var ref;
                defaults = $.extend(defaults, options);
                if ( methods.hasExternalReferrer() ) {
                    ref = methods.checkReferrer();
                    if ( ref ) {
                        methods.incrementVisit(ref);
                    }
                }
            },
            /**
             * reset the storage
             * @memberOf referrerCount
             * @public
             * @category Function
            */
            resetStorage: function() {
                localStorage.removeItem( defaults.storageName );
            }
        };

    $.fn.referrerCount = function( arg ) {
        if( hasLocalstorage() ) {
            if ( methods[ arg ] ) {
                return methods[ arg ].apply( this, Array.prototype.slice.call( arguments, 1 ) );
            } else if ( typeof method === 'object' || ! arg ) {
                return methods.init.apply( this, arguments );
            } else {
                $.error( 'Method ' + arg + ' does not exist on jQuery.referrerCount' );
            }
        } else {
            return this;
        }
    };

})( jQuery, window, document );
