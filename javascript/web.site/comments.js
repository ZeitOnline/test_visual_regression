/**
 * @fileOverview Module for comments
 * @version  0.1
 */
/**
 * comments.js: module for comments
 * @module comments
 */
define([ 'jquery' ], function( $ ) {

    var $comments = $( '#comments' ),
        $commentsBody = $( '#js-comments-body' ),
        $commentForm = $( '#comment-form' ),
        slideDuration = 300,
        startEvent = ( 'ontouchstart' in window ) ? 'touchstart' : 'click',
        inputEvent = ( 'oninput' in document.createElement( 'input' )) ? 'input' : 'keypress',

    /**
     * comments.js: reply to comment
     * @function replyToComment
     */
    replyToComment = function( e ) {
        var cid  = this.getAttribute( 'data-cid' ),
            comment = $( this ).closest( '.comment__container' ),
            form = comment.find( '.js-reply-form' );

        e.preventDefault();
        this.blur();

        if ( !form.length ) {
            form = $commentForm
                .clone()
                .removeAttr( 'id' )
                .addClass( 'js-reply-form' )
                .css( 'display', 'none' )
                .appendTo( comment );
            form.find( 'textarea[name="comment"]' ).attr( 'placeholder', 'Ihre Antwort' );
            form.find( 'input[type="submit"]' ).prop( 'disabled', true ).val( 'Antworten' );
            form.find( 'input[name="pid"]' ).val( cid );
        }

        showForm( form, comment );
    },

    /**
     * comments.js: cancel reply to comment
     * @function cancelReply
     * @param  {object} e event object
     */
    cancelReply = function( e ) {
        e.preventDefault();

        $( this ).closest( '.js-reply-form' ).velocity( 'slideUp', slideDuration );
    },

    /**
     * comments.js: report comment
     * @function reportComment
     */
    reportComment = function( e ) {
        var cid  = this.getAttribute( 'data-cid' ),
            comment = $( this ).closest( '.comment__container' ),
            form = comment.find( '.js-report-form' ),
            template;

        e.preventDefault();
        this.blur();

        if ( !form.length ) {
            template = $( '#js-report-comment-template' ).html();
            form = $( template )
                .removeAttr( 'id' )
                .addClass( 'js-report-form' )
                .css( 'display', 'none' )
                .appendTo( comment );
            form.find( 'input[type="submit"]' ).prop( 'disabled', true );
            form.find( 'input[name="pid"]' ).val( cid );
        }

        showForm( form, comment );
    },

    /**
     * comments.js: recommend comment
     * @function recommendComment
     */
    recommendComment = function( e ) {
        var cid  = this.getAttribute( 'data-cid' ),
            link = $( this ),
            comment = link.closest( '.comment__container' ),
            sendurl = window.location.href,
            authenticated = $commentForm.hasClass( 'comment-form' ),
            form,
            template;

        e.preventDefault();
        this.blur();

        if ( !authenticated ) {
            form = comment.find( '.js-recommend-form' );

            if ( !form.length ) {
                template = $( '#js-report-comment-template' ).html().replace( /zu melden./, 'zu empfehlen.' );
                form = $( template )
                    .addClass( 'js-recommend-form' )
                    .css( 'display', 'none' )
                    .appendTo( comment );
            }

            showForm( form, comment );
            return false;
        }

        if ( link.hasClass( 'comment__reaction--sending' ) ) {
            return false;
        }

        hideOtherForms();
        link.addClass( 'comment__reaction--sending' );

        $.ajax({
            url: sendurl,
            data: {
                'ajax':     'true',
                'action':   'recommend',
                'pid':      cid
            },
            dataType: 'json',
            method: 'POST',
            success: function( response ) {
                if ( response ) {
                    link.removeClass( 'comment__reaction--sending' );

                    if ( response.response.error === false ) {
                        toggleRecommendationLink( link );
                        comment
                            .find( '.js-comment-recommendations' )
                            .html( response.response.recommendations )
                            .parent().css( 'display', response.response.recommendations ? '' : 'none' );
                    } else {
                        // what else?
                    }
                }
            }
        });

    },

    /**
     * comments.js: toggle recommendation link
     * @function toggleRecommendationLink
     * @param  {object} link    jQuery object
     */
    toggleRecommendationLink = function( link ) {
        var label;

        if ( link.hasClass( 'comment__reaction--active' )) {
            label = 'Empfehlen';
        } else {
            label = 'Empfohlen';
        }

        link.toggleClass( 'comment__reaction--active' )
            .find( '.comment__action' ).attr( 'title', label ).html( label );
    },

    /**
     * comments.js: show form
     * @function showForm
     * @param  {object} form    jQuery object
     * @param  {object} comment jQuery object
     */
    showForm = function( form, comment ) {
        var animation = 'slideUp';

        if ( form.is( ':hidden' ) ) {
            hideOtherForms();
            animation = 'slideDown';
        }

        form.velocity( animation, slideDuration, function() {
            form.find( 'textarea' ).focus();
        });
    },

    /**
     * comments.js: cancel report
     * @function cancelReport
     * @param  {object} e event object
     */
    cancelReport = function( e ) {
        e.preventDefault();

        $( this ).closest( '.js-report-form' ).velocity( 'slideUp', slideDuration );
    },

    /**
     * comments.js: submit report
     * @function submitReport
     * @param  {object} e event object
     */
    submitReport = function( e ) {
        e.preventDefault();

        var sendurl = window.location.href,
            form = this.form,
            input = this.form.elements;

        // avoid repeated submits
        $( this ).prop( 'disabled', true );

        $.ajax({
            url: sendurl,
            data: {
                'ajax':     'true',
                'action':   'report',
                'pid':      input.pid.value,
                'comment':  input.comment.value
            },
            dataType: 'json',
            method: 'POST',
            success: function( response ) {
                if ( response ) {
                    if ( response.response.error === false ) {
                        var $form = $( form ),
                            html = $( '#js-report-success-template' ).html(),
                            height = $form.css( 'height' ),
                            newHeight;

                        $form.html( html );

                        newHeight = $form.css( 'height' );

                        $form
                            .css( 'height', height )
                            .velocity({ height: newHeight }, function() {
                                $form.css( 'height', '' );
                            });
                    } else {
                        // what else?
                    }
                }
            }
        });
    },

    /**
     * comments.js: submit comment
     * @function submitComment
     * @param  {object} e event object
     */
    submitComment = function( e ) {
        e.preventDefault();

        var $form = $( this ),
            input = this.elements,
            sendurl = window.location.href;

        $form.find( '.comment-form__hint' ).removeClass( 'comment-form__hint--error' );
        $form.find( '.comment-form__input' ).removeClass( 'error' );
        $form.find( '.comment-form__error' ).removeClass( 'comment-form__error--visible' );

        if ( input.username && /^\s*$/.test( input.username.value ) ) {
            $form.find( '.comment-form__hint' ).addClass( 'comment-form__hint--error' );
            input.username.focus();
            return false;
        }

        var data = {
            'ajax':      'true',
            'action':    'comment',
            'pid':       input.pid.value,
            'comment':   input.comment.value
        };

        if ( input.username ) {
            data.username = input.username.value;
        }

        $.ajax({
            url: sendurl,
            dataType: 'json',
            data: data,
            method: 'POST',
            success: function( response ) {
                if ( response ) {
                    if ( response.error === 'username_exists_or_invalid' ) {
                        var input = $form.find( '.comment-form__input' ),
                            error = $form.find( '.comment-form__error' );

                        if ( error.length === 0 ) {
                            error = $( '<div></div>' ).addClass( 'comment-form__error' )
                                .text( 'Dieser Benutzername ist bereits vergeben oder enthält ungültige Zeichen.' )
                                .insertAfter( input );
                        }

                        error.addClass( 'comment-form__error--visible' );
                        input.addClass( 'error' );
                    } else {
                        window.location.href = response.location;
                    }
                }
            }
        });
    },

    /**
     * comments.js: enable form submit button
     * @function enableForm
     * @param  {object} e event object
     */
    enableForm = function() {
        var blank = /^\s*$/.test( this.value );

        $( this.form ).find( '.button' ).prop( 'disabled', blank );
    },

    /**
     * comments.js: hide other forms
     * @function hideOtherForms
     */
    hideOtherForms = function() {
        $commentsBody
            .find( 'form' )
            .filter( ':visible' )
            .velocity( 'slideUp', slideDuration );
    },

    /**
     * comments.js: initialize
     * @function init
     */
    init = function() {

        if ( !$comments.length ) {
            return;
        }

        var uid = $commentForm.attr( 'data-uid' );

        // highlight recommended comments for logged in user
        if ( uid ) {
            $commentsBody.find( '.js-recommend-comment' ).each( function() {
                var fans = this.getAttribute( 'data-fans' );

                fans = fans.length ? fans.split( ',' ) : [];

                if ( fans.indexOf( uid ) !== -1 ) {
                    toggleRecommendationLink( $( this ) );
                }
            });
        }

        // disable submit buttons of required fields
        $comments.find( '.js-required' ).each( enableForm );

        // register event handlers
        $comments.on( 'submit', '.js-submit-comment', submitComment );
        $commentsBody.on( startEvent, '.js-reply-to-comment', replyToComment );
        $commentsBody.on( startEvent, '.js-cancel-reply', cancelReply );
        $commentsBody.on( startEvent, '.js-report-comment', reportComment );
        $commentsBody.on( startEvent, '.js-cancel-report', cancelReport );
        $commentsBody.on( startEvent, '.js-submit-report', submitReport );
        $commentsBody.on( startEvent, '.js-recommend-comment', recommendComment );
        $comments.on( inputEvent, '.js-required', enableForm );
    };

    return {
        init: init
    };

});
