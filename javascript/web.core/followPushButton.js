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

            if ( !window.Zeit.isWrapped ) {
                return;
            }

            var followButtons = document.querySelectorAll( '.js-FollowPush' ),
                i;

            for ( i = 0; i < followButtons.length; i++ ) {

                var buttonContainer = followButtons[ i ],
                    taggroup = buttonContainer.getAttribute( 'data-followpush-taggroup' ) || null,
                    tag = buttonContainer.getAttribute( 'data-followpush-tag' ) || null;

                if ( taggroup && tag ) {
                    buttonContainer.innerHTML = '<a href="zeitapp://subscribe/' + taggroup + '/' + tag + '" class="button">Folgen</a>';
                }
            }
        }
    };
});
