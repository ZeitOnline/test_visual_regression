/* global console, alert */
(function( $ ){

	/**
	 * plugin to integrate video player
	 */
	$.fn.switchVideo = function() {

		var el = {
			/**
			 * build html for player object
			 * @param {Object} that
			 */
			buildPlayer: function( that ){

				if( el.id ){
					var playerObj = '<div class="video__wrapper" data-video='+el.id+'><div style="display:none"></div>' +
					'<object id="myExperience' +el.id+ '" class="BrightcoveExperience">' +
					'<param name="htmlFallback" value="true" />' +
					'<param name="bgcolor" value="#FFFFFF" />' +
					'<param name="width" value="580" />' +
					'<param name="height" value="327" />' +
					'<param name="playerID" value="2922359108001" />' +
					'<param name="playerKey" value="AQ~~,AAAABDk7jCk~,Hc7JUgOccNpvlYo3iMVDRDd9PQS2LC9K" />' +
					'<param name="isVid" value="true" />' +
					'<param name="isUI" value="true" />' +
					'<param name="dynamicStreaming" value="true" />' +
					'<param name="@videoPlayer" value="' +el.id+ '" />' +
					'<param name="autoStart" value="true" />' +
					'</object></div>';

					var parent = $( that ).parent();
					parent.empty();
					parent.css({ 'width': '100%', 'float': 'none' });
					parent.prepend( playerObj );
					window.brightcove.createExperiences();
				}
			},
			/**
			 * grab video id from meta data and store it
			 * @param  {Object} that
			 */
			buildId: function( that ){
				el.id = $( that ).closest( "figure[data-video]" ).attr( "data-video" );
			},
			/**
			 * add show/hide event for video still image and button
			 * @param {Object} that
			 */
			addEvent: function( that ){
				$( that ).find( "img, .video__button" ).on( "click", function( ev ){
					ev.preventDefault();
					el.buildId( this );
					el.buildPlayer( this );
				});
			},
			/**
			 * add play button to image
			 * @param {Object} that
			 */
			addButton: function( that ){
				if( el.id ){
					$( that ).find( '.video__button' ).addClass( 'icon-playbutton' );
				}
			},
			id: false
		};

		/**
		 * run through data-video elements
		 */
		$(this).each(function(){
			el.buildId( this );
			el.addButton( this );
			el.addEvent( this );
		});
	};
})( jQuery );
