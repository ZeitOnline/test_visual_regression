/* global console */
(function() {
	var Fontloader;
	Fontloader = (function() {
		function Fontloader() {
			// set up all font packages we need
			var font_dictionary = [
				{
					identifier: 'base',
					has_priority: true,
					path: '/css/standalone-fonts/base.css'
				},
				{
					identifier: 'quotes',
					selectors: ['.quote', '.quote--loud'],
					has_priority: false,
					path: '/css/standalone-fonts/quotes.css'
				}
			];
			var ua = window.navigator.userAgent,
			storage_base_string = 'de.zeit.zmo__webfonts--';

			// detect old browsers that won’t support woff anyways
			// alternative: ('querySelector' in document && 'localStorage' in window && 'addEventListener' in window)
			var is_old_browser = ua.indexOf( "Android" ) > -1 && ua.indexOf( "like Gecko" ) > -1 && ua.indexOf( "Chrome" ) === -1 || window.document.documentElement.className.indexOf( "lt-ie9" ) > -1,
			inject_ref = window.document.getElementsByTagName( "link" )[0];

			function append_css(style) {
				// create a style tag in the <head> filled with raw font-face declarations
				var style_tag = window.document.createElement( "style" );
				style_tag.innerHTML = style;
				if( inject_ref && inject_ref.parentNode ) {
					inject_ref.parentNode.insertBefore( style_tag, inject_ref );
				}
			}

			function fetch_css(path, identifier, font_data) {
				// if we already have font_data (from localstorage), make use of it immediately
				if (font_data && font_data.length > 0) {
					append_css(font_data);
				} else {
					// nope, we don’t: let’s fetch it asynchronously from the server
					$.ajax({
						url: path,
						success: function (ajaxed_style) {
							// we’ve got the fonts, store them in localstorage and apply them
							localStorage.setItem(storage_base_string + identifier, ajaxed_style);
							append_css(ajaxed_style);
						}
					});
				}
			}

			function init_fonts() {
				var scheduled_fonts = [];
				for (var i in font_dictionary) {
					if (i) {
						var pack = font_dictionary[i];
						pack.data = localStorage.getItem(storage_base_string + pack.identifier);
						// if pack has priority or data is already in localstorage: apply immediately
						if (pack.has_priority || pack.data) {
							// drop it in as fast as possible
							fetch_css(pack.path, pack.identifier, pack.data);
						} else {
							// schedule for later lazy loading
							scheduled_fonts.push(font_dictionary[i]);
						}
					}
				}
				// lazy load fonts at last
				window.onload = function() {
					for (var i in scheduled_fonts) {
						if (i) {
							fetch_css(scheduled_fonts[i].path, scheduled_fonts[i].identifier);
						}
					}
				};
			}

			// only load webfont css when we have a good guesstimate that the browser will support woff
			if (!is_old_browser) {
				init_fonts();
			}

		}

		return Fontloader;

	})();
	return new Fontloader();
})();
