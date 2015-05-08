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
            form.get( 0 ).elements.comment.placeholder = 'Ihre Antwort';
            form.find( 'input[type="submit"]' ).prop( 'disabled', true ).val( 'Antworten' );
            form.find( 'input[name="cid"]' ).val( cid );
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

        $( this ).closest( '.js-reply-form' ).slideUp( slideDuration );
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
                .addClass( 'js-report-form' )
                .css( 'display', 'none' )
                .appendTo( comment );
            form.find( 'input[type="submit"]' ).prop( 'disabled', true );
            form.find( 'input[name="cid"]' ).val( cid );
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

        hideOtherForms();
        link.find( '.comment__icon' ).addClass( 'comment__icon--sending' );

        $.ajax({
            url: sendurl,
            data: {
                'ajax':     'true',
                'action':   'recommend',
                'cid':      cid
            },
            dataType: 'json',
            method: 'POST',
            success: function( response ) {
                if ( response ) {
                    if ( response.response.error === false ) {
                        var recommendations = comment.find( '.comment__recommendations' ),
                            number = recommendations.html().replace( /\D+/g, '' ) || 0,
                            stars;

                        number = toggleRecommendationLink( link, number );
                        stars = number ? number + ' &#9733;' : '';
                        recommendations.html( stars );
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
     * @param  {int} number     number of recommendations
     */
    toggleRecommendationLink = function( link, number ) {
        var label;

        if ( link.hasClass( 'comment__reaction--active' )) {
            label = 'Empfehlen';
            --number;
        } else {
            label = 'Empfohlen';
            ++number;
        }

        link.toggleClass( 'comment__reaction--active' )
            .find( '.comment__icon' )
            .toggleClass( 'icon-comment-reactions-recommend' )
            .toggleClass( 'icon-comment-reactions-recommend-active' )
            .removeClass( 'comment__icon--sending' );
        link.find( '.comment__action' ).attr( 'title', label ).html( label );

        return number;
    },

    /**
     * comments.js: show form
     * @function showForm
     * @param  {object} form    jQuery object
     * @param  {object} comment jQuery object
     */
    showForm = function( form, comment ) {
        if ( form.is( ':hidden' ) ) {
            hideOtherForms();
        }

        form.slideToggle( slideDuration, function() {
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

        $( this ).closest( '.js-report-form' ).slideUp( slideDuration );
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
                'cid':      input.cid.value,
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
                            .animate({ height: newHeight });
                    } else {
                        // what else?
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
        $commentsBody.find( 'form' ).filter( ':visible' ).slideToggle( slideDuration );
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
        $comments.find( '.js-required' ).each( function() {
            $( this.form ).find( '.button' ).prop( 'disabled', true );
        });

        // register event handlers
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
