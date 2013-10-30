/* global console */
(function() {
	var Fontloader;
	Fontloader = (function() {

		function Fontloader() {
			var font_path = "/css/webfonts.css",
			ua = window.navigator.userAgent;

			// detect old browsers that won’t support woff anyways
			// alternative: ('querySelector' in document && 'localStorage' in window && 'addEventListener' in window)
			var is_old_browser = ua.indexOf( "Android" ) > -1 && ua.indexOf( "like Gecko" ) > -1 && ua.indexOf( "Chrome" ) === -1 || window.document.documentElement.className.indexOf( "lt-ie9" ) > -1,
			inject_ref = window.document.getElementsByTagName( "link" )[0];

			function insert_css(style) {
				// create a style tag in the <head> filled with raw font-face declarations
				var style_tag = window.document.createElement( "style" );
				style_tag.innerHTML = style;
				if( inject_ref && inject_ref.parentNode ) {
					inject_ref.parentNode.insertBefore( style_tag, inject_ref );
				}
			}

			function load_css() {
				// first determine whether we have cached fonts in localstorage
				var local_style = localStorage.getItem('zeit_webfonts');
				if (local_style && local_style.length > 0) {
					// yep, we do, so drop them in
					insert_css(local_style);
				} else {
					// nope, we don’t: let’s fetch them from the server
					$.ajax({
						url: font_path,
						success: (function (ajaxed_style) {
							// we’ve got the fonts, store them in localstorage and apply them
							localStorage.setItem('zeit_webfonts', ajaxed_style);
							insert_css(ajaxed_style);
						})
					});
				}
			}

			// only load webfont css when we have a good guesstimate that the browser will support woff
			if (!is_old_browser) {
				load_css();
			}
		}

		return Fontloader;

	})();
	return new Fontloader();
})();
