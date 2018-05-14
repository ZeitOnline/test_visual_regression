/**
 * @fileOverview Module for inserting follow(-push-notifications)-buttons into
 * pages and manipulating them based on browser capabilities, environment,
 * and user status.
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
define([ ], function() {
    return {
        init: function() {

            if ( !window.Zeit.isWrapped || !window.PushManager ) {
                return;
            }

            var followButtons = document.querySelectorAll( '.js-FollowPush' ),
                i;

            if ( followButtons ) {
                for ( i = 0; i < followButtons.length; i++ ) {
                    followButtons[ i ].innerHTML = '<a href="zeitapp://subscribe/authors/[author-id]" class="button">Folgen</a>';
                }
            }
        }
    };
});
