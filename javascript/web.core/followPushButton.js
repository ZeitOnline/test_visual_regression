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

                    var buttonContainer = followButtons[ i ],
                        segment = buttonContainer.getAttribute( 'data-followpush-segment' ) || null,
                        id = buttonContainer.getAttribute( 'data-followpush-id' ) || null;

                    if ( segment && id ) {
                        buttonContainer.innerHTML = '<a href="zeitapp://subscribe/' + segment + '/' + id + '" class="button">Folgen</a>';
                    }


                }
            }
        }
    };
});
