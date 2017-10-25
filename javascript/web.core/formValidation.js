// enable button when reCaptcha is solved
function enableButton() {
    document.getElementById( 'formsubmit' ).disabled = false;
}
window.enableButton = enableButton;
document.getElementById( 'formsubmit' ).disabled = true;

// validate inputfields
function formValidation() {
    var feedbackError = document.getElementById( 'feedbackerror' ); // error msg
    var feedbackErrorTextarea = document.getElementById( 'feedbackerrortextarea' ); // error msg
    var feedbacktext = document.getElementById( 'feedbacktext' ); // textarea

    // configure inputfields
    var validationInfo = {
        'feedbacktext': {
            'required': true }
    };

    // remove errormsg when user filling in the textarea
    feedbacktext.addEventListener( 'keyup', function() {
        feedbackError.style.display = 'none';
        feedbackErrorTextarea.style.display = 'none';
        feedbacktext.className = 'feedback-form__textarea';
    });

    // remove required attribute for js version
    feedbacktext.removeAttribute( 'required' );

    // function to check the inputfields
    document.feedbackform.onsubmit = function() {
        var key;
        for ( key in validationInfo ) {
            if ( key ) {
                var feedbackField = document.getElementById( key );

                // if value for textfield isn't set
                if ( ( validationInfo[ key ].required ) && ( feedbackField.value === '' ) ) {
                    feedbackError.innerHTML = 'Bitte überprüfen Sie Ihre Eingaben.';
                    feedbackErrorTextarea.innerHTML = 'Bitte geben Sie eine Nachricht ein.';
                    feedbackError.style.display = 'block';
                    feedbackErrorTextarea.style.display  = 'block';
                    feedbacktext.className = 'feedback-form__bgerror';
                    feedbackField.select();
                    return false;
                }
            }
        }
        // if value is valid then submit form
        return true;
    };
}

formValidation();
