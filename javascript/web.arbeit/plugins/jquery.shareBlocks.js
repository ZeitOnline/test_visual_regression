/**
 * @fileOverview jQuery Plugin for calling the Sharebert feature on
 * article blocks.
 * @author thomas.puppe@zeit.de
 * @version 0.1
 */
( function( $, Zeit ) {

    'use strict';

    // TODO: check the object vs prototype thing

    var settings = {
            sharebertUrl: 'http://share.zeit.de/-/apps/island/shots'
        },
        defaults = {
            duration: 200
        },
        sharebertRedirectUrl,
        sharebertShotUrl;

    function log( message ) {
        window.console.debug( message );
    }

    function share( event ) {
        var $elem = $( event.target ).closest( '.js-shareblock' );
        console.debug( event );
        console.debug( $elem );
        sharebertRedirectUrl = $elem.data( 'sharebert-redirect-url' ); // TODO: without params usw
        sharebertShotUrl = $elem.data( 'sharebert-screenshot-target' );
        log( 'sharebertRedirectUrl: ' + sharebertRedirectUrl );
        log( 'sharebertShotUrl: ' + sharebertShotUrl );
        event.preventDefault(); // TODO: optimize via passive-thing
    }

    function initShareBlocks( element ) {
        log( 'initialize click event on ' + element );
        element.addEventListener( 'click', share );
    }

    $.fn.shareBlocks = function( options ) {
        settings = $.extend({}, defaults, options );

        log( 'setup with ' + Zeit + ' and ' + settings );

        return this.each( function() {
            initShareBlocks( this );
        });
    };
})( jQuery, window.Zeit );

/*

<script type="text/javascript">
var sharebertUrl = "http://share.zeit.de/-/apps/island/shots",
redirectURL = window.location.href;
window.Zeit.require(['jquery'], function(jqr){
  function addBigShareButtons(url) {
      var campaignCode = {
          wt_zmc: null,
          utm_medium: 'sm',
          utm_source: null,
          utm_campaign: 'ref',
          utm_content: 'zeitde_dskshare_link_x',
          t: document.title
      };
      function shareUrl(url) {
          window.open(url, '', 'menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=300,width=600');
      }
      jqr('.tb-newShareBox').css( "display", "inline-block");
      jqr('#facebook-share').on('click', function() {
          if (wt) {
              wt.sendinfo({ linkId: 'stationaer.articlebottom.1.1.social.facebook|https://www.facebook.com/sharer/sharer.php?u=' + url });
          }
          campaignCode.wt_zmc = 'sm.ext.zonaudev.facebook.ref.zeitde.dskshare.link.x';
          campaignCode.utm_source = 'facebook_zonaudev_ext';
          shareUrl('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent( url + '?' + jqr.param(campaignCode) ));
      });
      jqr('#twitter-share').on('click', function(){
          if (wt) {
              wt.sendinfo({ linkId: 'stationaer.articlebottom.1.2.social.twitter|https://twitter.com/intent/tweet?url=' + url });
          }
          campaignCode.wt_zmc = 'sm.ext.zonaudev.twitter.ref.zeitde.dskshare.link.x';
          campaignCode.utm_source = 'twitter_zonaudev_ext';
          shareUrl('https://twitter.com/intent/tweet?text=%23generatorsson&url=' +
            encodeURIComponent( url + '?' + jqr.param(campaignCode) ));
      });
  }
  var info = {};

  jqr('button.submit-name').on('click', function(event){
    var loadingImage = '<div class="loadingImage pulse"></div>'

    event.preventDefault();

    if (jqr('p.errorMessage').length > 0) {
      jqr('p.errorMessage').remove();
    }
    info['vorname'] = jqr('input.vorname').val();
    info['vatername'] = jqr('input.vatername').val();
    info['geschlecht'] = jqr('select.geschlecht').val();
    jqr('div.generatorson').append(loadingImage);
    var targetURL = "http://live0.zeit.de/em-2016/islandtrikot.html?" + jqr.param( info );
    console.log(info);
    var metaData = {
      "title": "So würde ich für Island auflaufen",
      "description": "Und Sie? Generieren Sie sich Ihren isländischen Namen auf ZEIT ONLINE. #generatorsson",
      "vorname": info.vorname,
      "vatername": info.vatername,
      "geschlecht": info.geschlecht
    };
    var myData = {
      "target_url": targetURL,
      "meta_data": metaData,
      "redirect_to": redirectURL
    };
    jqr.ajax({
      url: sharebertUrl,
      type: "POST",
      data: JSON.stringify( myData ),
      processData: false,
      contentType: "application/json; charset=utf-8",
      dataType: "json"
    }).done(
      function( data ) {
        console.log( 'success', data );
        var imgMarkup = '<img class="generatorson__img" src="' + data.src_url + '/1200x628.png">';
        var shareImgHght = jqr('.generatorson__img').height();
        if(jqr('img.generatorson__img').length > 0){
          jqr('img.generatorson__img').remove();
        }
        jqr('div.generatorson').append(imgMarkup);
        jqr('.generatorson__img').on('load', function() {
          jqr('div.loadingImage').remove();
          jqr('.generatorson__img').show();
          addBigShareButtons(data.src_url);
          jqr('div.tb-newShareBox').show();
        });
      }
    ).fail(
      function( jqXHR, textStatus, errorThrown ) {
        var errorMessage = '<p class="errorMessage paragraph">😱 Generatorsson kommt ins Schwitzen!' +
        '<br>Leider ist ein Fehler aufgetreten, bitte versuchen Sie es später noch einmal.</p>';
        jqr('div.loadingImage').remove();
        if (jqr('p.errorMessage').length > 0) {} else {
          jqr('div.generatorson').append(errorMessage);
        }
        console.log( 'error', jqXHR );
      }
    );
  });
})
</script>

*/
