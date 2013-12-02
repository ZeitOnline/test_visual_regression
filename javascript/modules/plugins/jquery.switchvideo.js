/* switch between image and video player */

(function( $ ){

	$.fn.switchVideo = function() {

		var el = {

			//build Playerobject
			buildPlayer: function( that ){

				if( el.id ){
					var playerObj = '<div class="video__wrapper"><div style="display:none"></div>' +
					'<object id="myExperience' +el.id+ '" class="BrightcoveExperience">' +
					'<param name="htmlFallback" value="true" />' +
					'<param name="bgcolor" value="#FFFFFF" />' +
					'<param name="width" value="580" />' +
					'<param name="height" value="327" />' +
					'<param name="playerID" value="71289488001" />' +
					'<param name="playerKey" value="AQ~~,AAAABDk7jCk~,Hc7JUgOccNp4D5O9OupA8T0ybhDjWLSQ" />' +
					'<param name="isVid" value="true" />' +
					'<param name="isUI" value="true" />' +
					'<param name="dynamicStreaming" value="true" />' +
					'<param name="@videoPlayer" value="' +el.id+ '" />' +
					'<param name="includeAPI" value="false" />' +
					'<param name="autoStart" value="true" />' +
					'</object></div>';

					var parent = $( that ).parent();
					parent.empty();
					parent.css({ 'width': '100%', 'float': 'none' });
					parent.prepend( playerObj );
					window.brightcove.createExperiences();
				}
			},
			//add show/hide event
			addEvent: function( that ){
				$( that ).find( "img, .figure__video__button" ).on( "click", function( ev ){
					ev.preventDefault();
					el.buildPlayer( this );
				});
			},
			//add play button to image
			addButton: function( that ){
				if( el.id ){
					$( that ).find( '.figure__video__button' ).addClass( 'icon-playbutton' );
				}
			},
			//grab meta data
			buildId: function( that ){
				el.id = $( that ).attr( "data-video" );
			},
			//trigger player if flash isnt enabled, to avoid douple tap 
			testForFlash: function( that ){
				var hasFlash = false;

				try {
					var flash = new window.ActiveXObject('ShockwaveFlash.ShockwaveFlash');
					if( flash ){
						hasFlash = true;
					}
				}catch(e){
					if(navigator.mimeTypes ["application/x-shockwave-flash"] !== undefined){
						hasFlash = true;
					}
				}

				if( !hasFlash ){
					$( that ).find( ".figure__video__button" ).remove();
					$( that ).find( "img" ).trigger( "click" );
				}
			},
			//stored video id
			id: false
		};
				//run through data-video elements
		$(this).each(function(){
			el.buildId( this );
			el.addButton( this );
			el.addEvent( this );
			el.testForFlash( this );
		});
	};
})( jQuery );