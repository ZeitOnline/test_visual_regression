/**
 * @fileOverview jQuery Plugin for additional functionality in infoboxes
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
(function( $, win ) {
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
    * additional functionality for otherwise css powered infoboxes
    * @class infobox
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.infobox = function() {
        var pos,
            ltIE9 = ( $( 'html.lt-ie9' ).size() > 0 ),
            id = $( this ).attr( 'id' ),
            $that = $( this ),
            ariaState = '',
            /**
             * changeAriaState sets initially and based on tab/accordion aria features
             * @param  {bool} initial triggers initial setting of aria-hidden in tabs
             */
            changeAriaState = function( initial ) {
                // expose aria relationships based on visibility of acordion/tabs
                if ( $( '.infobox__navigation:visible' ).size() > 0 && ariaState !== 'tabs' ) {
                    // remove possible accordion rel
                    $that.find( '.infobox__tab' ).find( '*[role=tab]' ).each( function( n ) {
                        $( this ).attr( 'aria-controls', '' );
                    });
                    // add/change tabs rels
                    $that.find( '*[role=tabpanel]' ).each( function( n ) {
                        if ( initial && n === 0 ) {
                            $( this ).attr( 'aria-hidden', 'false' );
                        }
                        $( this ).attr( 'aria-labelledby', id + '-' + ( n + 1 ) + '-tablabel' );
                    });
                    // labels
                    $that.find( '.infobox__navigation' ).find( '*[role=tab]' ).each( function( n ) {
                        $( this ).attr( 'aria-controls', id + '-' + ( n + 1 ) + '-panel' );
                    });
                    ariaState = 'tabs';
                } else if ( ariaState !== 'accordion' ) {
                    // remove possible tabs rel
                    $that.find( '.infobox__navigation' ).find( '*[role=tab]' ).each( function( n ) {
                        $( this ).attr( 'aria-controls', '' );
                    });
                    // add/change accordion rels
                    $that.find( '*[role=tabpanel]' ).each( function( n ) {
                        if ( $( this ).height() === 0 ) {
                            $( this ).attr( 'aria-hidden', 'true' );
                        } else {
                            $( this ).attr( 'aria-hidden', 'false' );
                        }
                        $( this ).attr( 'aria-labelledby', id + '-' + ( n + 1 ) + '-label' );
                    });
                    $that.find( '.infobox__tab' ).find( '*[role=tab]' ).each( function( n ) {
                        $( this ).attr( 'aria-controls', id + '-' + ( n + 1 ) + '-panel' );
                    });
                    ariaState = 'accordion';
                }
            },
            changeAriaHiddenState = function( $elem, tabs ) {
                if ( tabs ) {
                    $( '.infobox__tab .infobox__inner' ).attr( 'aria-hidden', 'true' );
                    $elem.attr( 'aria-hidden', 'false' );
                } else {
                    $elem.attr( 'aria-hidden', function( i, val ) {
                        return val === 'false' ? 'true' : 'false';
                    });
                }
            };

        return this.each( function() {
            // fallback for ie lower 9
            if ( ltIE9 ) {
                $( '.infobox__tab' ).eq( 0 ).find( '.infobox__inner' ).addClass( 'infobox__inner--active' );
            }
            // actions following click on tab
            $( '.infobox__navlabel' ).on( 'click', function( evt ) {
                $( '.infobox__navlabel.infobox__navlabel--checked' ).removeClass( 'infobox__navlabel--checked' );
                $( evt.target ).addClass( 'infobox__navlabel--checked' );
                $( '.infobox__navlabel[aria-selected=true]' ).attr( 'aria-selected', 'false' );
                $( evt.target ).attr( 'aria-selected', 'true' );
                // aria hidden on/off and IE9 classing
                pos = $( evt.target ).parent().prevAll().size();
                changeAriaHiddenState( $( '.infobox__tab' ).eq( pos ).find( '.infobox__inner' ), true );
                if ( ltIE9 ) {
                    // fallback for ie lower 9
                    $( '.infobox__tab .infobox__inner' ).removeClass( 'infobox__inner--active' );
                    $( '.infobox__tab' ).eq( pos ).find( '.infobox__inner' ).addClass( 'infobox__inner--active' );
                }

            });
            // actions following click on accordion title
            $( '.infobox__title .infobox__label' ).on( 'click', function( evt ) {
                changeAriaHiddenState( $( evt.target ).parent().next( 'article' ) );
            });
            // adding ARIA roles, first run
            changeAriaState( true );
            $( window ).on( 'resize', function() {
                changeAriaState();
            });
        });
    };
})( jQuery, window );
