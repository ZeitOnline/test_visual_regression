/**
 * @fileOverview Module for comments
 * @version  0.1
 */
/**
 * comments.js: module for comments
 * @module comments
 */
define([ 'jquery', 'velocity.ui', 'web.core/zeit' ], function( $, Velocity, Zeit ) {

    var $comments = $( '#comments' ),
        $commentsBody = $( '#js-comments-body' ),
        $commentForm = $( '#comment-form' ),
        uid = $commentForm.attr( 'data-uid' ),
        slideDuration = 300,
        inputEvent = ( 'oninput' in document.createElement( 'input' )) ? 'input' : 'keypress',
        sendurl = window.location.href,

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
            form.find( 'textarea[name="comment"]' ).attr( 'placeholder', 'Ihre Antwort' ).val( '' );
            form.find( 'input[type="submit"]' ).prop( 'disabled', true ).val( 'Antworten' );
            form.find( 'input[name="pid"]' ).val( cid );
            form.find( '.js-count-formchars' ).text( '' );
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

    promoteComment = function( e ) {
        var link = $( this ),
            action = link.data( 'action' ),
            cid  = link.data( 'cid' ),
            comment = link.closest( '.comment__container' ),
            failText = 'Empfehlung fehlgeschlagen, bitte Seite neu laden.';

        e.preventDefault();
        this.blur();

        if ( link.hasClass( 'comment__moderation--sending' ) ) {
            return false;
        }

        link.addClass( 'comment__moderation--sending' );

        $.ajax({
            url: sendurl,
            data: {
                'ajax':     'true',
                'action':   action,
                'pid':      cid
            },
            dataType: 'json',
            method: 'POST'
        })
        .done( function( response ) {
            if ( response ) {
                if ( response.response.error === false ) {
                    link.removeClass( 'comment__moderation--sending' );

                    if ( action === 'promote' ) {
                        link.text( 'Redaktionsempfehlung entfernen' )
                            .data( 'action', 'demote' );
                    }
                    if ( action === 'demote' ) {
                        link.text( 'Redaktionsempfehlung' )
                            .data( 'action', 'promote' );
                    }
                } else {
                    link.text( failText );
                }
            }
        })
        .fail( function() {
            link.text( failText );
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

        var form = this.form,
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
            input = this.elements;

        $form.find( '.comment-form__hint' ).removeClass( 'comment-form__hint--error' );
        $form.find( '.comment-form__input' ).removeClass( 'error' );
        $form.find( '.comment-form__error' ).removeClass( 'comment-form__error--visible' );

        if ( input.username && /^\s*$/.test( input.username.value ) ) {
            $form.find( '.comment-form__hint' ).addClass( 'comment-form__hint--error' );
            input.username.focus();
            return false;
        }

        // avoid repeated submits
        $form.find( '.button' ).prop( 'disabled', true );

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

                        // enable submit button again
                        $form.find( '.button' ).prop( 'disabled', false );
                    } else if ( response.response.premoderation ) {
                        var premoderation = $( $( '#premoderation-template' ).html().format( response.response.userName ) );
                        if ( response.response.setUser ) {
                            premoderation.find( '.show-set-user' ).show();
                        } else {
                            premoderation.find( '.show-set-user' ).hide();
                        }
                        premoderation.children( '.overlay' ).show();
                        premoderation.children( '.lightbox' ).show();
                        premoderation.find( '.lightbox-button' ).on( 'click', function() {
                            premoderation.detach();
                            if ( response.response.setUser ) {
                                window.location.hash = '#comment-form';
                                window.location.reload( true );
                            } else {
                                $form.find( '.comment-form__textarea' ).val( '' );
                                $form.find( '.button' ).prop( 'disabled', false );
                            }
                        });
                        $( '#comments' ).before( premoderation );
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

    putRewrapperOnReplies = function( $firstReply ) {
        var $rootComment = $firstReply.prev( '.comment' ),
            rewrapperId = $firstReply.data( 'rewrapper-id' ),
            rewrapper = '' +
            '<div id="' + rewrapperId + '" class="comment__rewrapper comment__rewrapper--loading js-hide-replies">' +
                '<span class="comment__count"></span>\n' +
                '<span class="comment__cta">Antworten verbergen</span>\n' +
            '</div>\n';

        $firstReply.find( '.comment__container' ).prepend( rewrapper );
    },

    updateRewrapperOnReplies = function( $firstReply ) {
        var $rootComment = $firstReply.prev( '.comment' ),
            rewrapperId = $firstReply.data( 'rewrapper-id' ),
            $answers = $rootComment.nextUntil( '.js-comment-toplevel', '.comment--indented' ),
            $rewrapper = $( '#' + rewrapperId );

        $rewrapper.find( '.comment__count' ).eq( 0 ).text( '− ' + $answers.length );
        $rewrapper.removeClass( 'comment__rewrapper--loading' );

    },

    wrapReplies = function() {
        // TODO: Target + Deeplinks testen
        var $rootComments = $commentsBody.find( '.js-comment-toplevel' ),
            $target;

        // TODO: wird das $target noch benötigt?
        if ( window.location.hash.indexOf( '#cid-' ) === 0 ) {
            $target = $( window.location.hash );
        }

        $rootComments.each( function() {
            var $root = $( this ),
                $replyLinkContainer = $root.nextUntil( '.js-comment-toplevel', '.js-comment-loader' ),
                $answers,
                id,
                replyLoadLink,
                replyLoadUrl,
                replyLoadFallbackUrl,
                replyCountElement,
                replyCountString,
                replyCountInteger,
                overlayHTML;

            if ( $replyLinkContainer.length === 0 ) {
                return;
            }

            $answers = $root.nextUntil( '.js-comment-toplevel', '.comment--indented' );
            id = 'hide-replies-' + this.id;
            replyLoadLink = $replyLinkContainer.find( 'a' );
            replyLoadUrl = replyLoadLink.data( 'url' );
            replyLoadFallbackUrl = replyLoadLink.attr( 'href' );
            replyCountElement = $replyLinkContainer.find( '.comment-overlay__count' );
            replyCountString = replyCountElement.eq( 0 ).text().replace( '+ ', '' );
            replyCountInteger = parseInt( replyCountString, 10 );

            overlayHTML = '' +
                '<div class="comment-overlay js-load-comment-replies" ' +
                    'data-url="' + replyLoadUrl + '" data-fallbackurl="' + replyLoadUrl + '">\n' +
                    '<div class="comment-overlay__wrap">\n' +
                        '<span class="comment-overlay__count">+ ' + replyCountInteger + '</span>\n' +
                        '<span class="comment-overlay__cta">Weitere Antworten anzeigen</span>\n' +
                    '</div>\n' +
                '</div>\n';

            $answers.eq( 0 )
                .data({
                    'reply-count': replyCountInteger,
                    'rewrapper-id': id })
                .addClass( 'comment--wrapped' )
                .find( '.comment__body' )
                .append( overlayHTML );

            $replyLinkContainer.remove();
        });
    },

    coverReply = function( $firstReply, replyCount ) {
        var overlayHTML = '' +
            '<div class="comment-overlay">\n' +
                '<div class="comment-overlay__wrap">\n' +
                    '<span class="comment-overlay__count">+ ' + replyCount + '</span>\n' +
                    '<span class="comment-overlay__cta">Weitere Antworten anzeigen</span>\n' +
                '</div>\n' +
            '</div>\n';

        $firstReply.addClass( 'comment--wrapped' )
            .find( '.comment__body' )
            .append( overlayHTML );
    },

    loadReplies = function( e ) {
        var $wrapped = $( this ),
            url = $wrapped.data( 'url' ),
            fallbackUrl = $wrapped.data( 'fallbackurl' ),
            $firstReply = $wrapped.closest( '.comment' ).removeClass( 'comment--wrapped' ),
            replyCountInteger = parseInt( $firstReply.data( 'reply-count' ), 10 ),
            placeholderWording = ( replyCountInteger === 1 ) ? 'Kommentar wird geladen.' : 'Kommentare werden geladen.',

            placeholderHTML = '' +
                '<article class="comment comment--indented js-comment-placeholder">' +
                    '<div class="comment__container comment__container--placeholder">' +
                        '<p class="js-comment-placeholder__content">' + placeholderWording + '</p></div>' +
                '</article>',
            repliesLoaded = false;

        e.preventDefault();

        // OPTIMIZE: Netter mit Promises arbeiten als dem Callback-vs-repliesLoaded-Quatsch?
        $.ajax({
            url: url,
            method: 'GET',
            success: function( response ) {
                repliesLoaded = true;
                $firstReply.nextUntil( '.js-comment-toplevel', '.js-comment-placeholder' ).remove();
                $firstReply.after( response );

                updateRewrapperOnReplies( $firstReply );
                adjustRecommendationLinks();

                // add community frontend moderation
                if ( uid && $commentForm.data( 'mod' ) === 'mod' ) {
                    $firstReply.nextUntil( '.js-comment-toplevel', '.comment' ).each( addModeration );
                }

            },
            complete: function( jqXhr, textStatus ) {
                if ( textStatus !== 'success' ) {
                    window.location.href = fallbackUrl;
                }
            }
        });

        putRewrapperOnReplies( $firstReply );

        // without the js-load-comment-replies class, we toggle existing
        // replies (instead of loading from server)
        $wrapped.removeClass( 'js-load-comment-replies' ).addClass( 'js-show-replies' );

        if ( !repliesLoaded ) {
            $firstReply.after( placeholderHTML );
        }

    },

    showReplies = function( e ) {
        var $wrapped = $( this ).closest( '.comment' ),
            selector = '#' + $wrapped.data( 'rewrapper-id' ),
            $link = $( selector ),
            $repliesToShow;

        e.preventDefault();
        $link.velocity( 'slideDown', slideDuration );
        $wrapped.removeClass( 'comment--wrapped' );
        // get other replies, filter to remove ads from result
        $repliesToShow = $wrapped.nextUntil( '.js-comment-toplevel', '.comment--indented' );
        // for performance reasons, we only slide the first items and simply show the other ones
        $repliesToShow.slice( 0, 5 ).velocity( 'slideDown', {
            'duration': slideDuration,
            'complete': function() {
                $repliesToShow.slice( 5 ).show();
            }
        } );

    },

    hideReplies = function() {
        var $root = $( this ).velocity( 'slideUp' ).closest( '.comment' ),
            $answers = $root.nextUntil( '.js-comment-toplevel', '.comment--indented' );

        $root.addClass( 'comment--wrapped' );
        $answers.slice( 0, 5 ).velocity( 'slideUp', {
            'duration': slideDuration,
            'complete': function() {
                $answers.slice( 5 ).hide();
            }
        } );
    },

    addModeration = function() {
        var $comment = $( this ),
            promoted = $comment.find( '.comment-meta__badge--promoted' ).length,
            action = promoted ? 'demote' : 'promote',
            actionLabel = promoted ? 'Redaktionsempfehlung entfernen' : 'Redaktionsempfehlung',
            cid = this.id.substr( 4 ),
            modHTML = '' +
            '<ul class="comment__moderations">' +
                '<li>' +
                    '<a class="comment__moderation" href="%ch%/comment/edit/%cid%">' +
                        'Kommentar bearbeiten' +
                    '</a>' +
                '</li>' +
                '<li>' +
                    '<a class="comment__moderation js-promote-comment" data-action="%action%" data-cid="%cid%" href="#' + this.id + '">' +
                        actionLabel +
                    '</a>' +
                '</li>' +
            '</ul>';

        modHTML = modHTML.replace( /%cid%/g, cid )
            .replace( '%action%', action )
            .replace( '%ch%', Zeit.communityHost );
        $comment.find( '.comment__reactions' )
            .append( modHTML );
    },

    jumpToComment = function() {
        var comment = $( this.hash );

        if ( comment.length ) {
            comment.scrollIntoView();
            return false;
        }
    },

    adjustRecommendationLinks = function() {

        if ( uid ) {
            // highlight recommended comments for logged in user
            $commentsBody.find( '.js-recommend-comment' ).each( function() {
                if ( uid === this.getAttribute( 'data-uid' ) ) {
                    // hide recommendation link for user's own comments
                    this.style.display = 'none';
                } else {
                    // highlight recommended comments for logged in user
                    var fans = this.getAttribute( 'data-fans' );

                    fans = fans.length ? fans.split( ',' ) : [];

                    if ( fans.indexOf( uid ) !== -1 ) {
                        toggleRecommendationLink( $( this ) );
                    }
                }
            });
        }

    },

    /**
     * comments.js: initialize
     * @function init
     */
    init = function() {

        if ( !$comments.length ) {
            return;
        }

        // disable submit buttons of required fields
        $comments.find( '.js-required' ).each( enableForm );

        // collapse consecutive replies
        wrapReplies();

        adjustRecommendationLinks();

        // add community frontend moderation
        if ( uid  && $commentForm.data( 'mod' ) === 'mod' ) {
            $commentsBody.find( '.comment' ).each( addModeration );
        }

        // register event handlers
        $comments.on( 'submit', '.js-submit-comment', submitComment );
        $commentsBody.on( 'click', '.js-reply-to-comment', replyToComment );
        $commentsBody.on( 'click', '.js-cancel-reply', cancelReply );
        $commentsBody.on( 'click', '.js-report-comment', reportComment );
        $commentsBody.on( 'click', '.js-cancel-report', cancelReport );
        $commentsBody.on( 'click', '.js-submit-report', submitReport );
        $commentsBody.on( 'click', '.js-recommend-comment', recommendComment );
        $commentsBody.on( 'click', '.js-show-replies', showReplies );
        $commentsBody.on( 'click', '.js-hide-replies', hideReplies );
        $commentsBody.on( 'click', '.js-promote-comment', promoteComment );
        $commentsBody.on( 'click', '.js-jump-to-comment', jumpToComment );
        $comments.on( inputEvent, '.js-required', enableForm );

        $commentsBody.on( 'click', '.js-load-comment-replies', loadReplies );
    };

    return {
        init: init
    };

});
