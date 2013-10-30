/* global console, alert */
(function() {
	var Fontloader;
	Fontloader = (function() {

		function Fontloader() {
			var fonts = "/css/webfonts.css",
			ua = window.navigator.userAgent;

			// alternative: 'querySelector' in document && 'localStorage' in window && 'addEventListener' in window
			var old_browser = ua.indexOf( "Android" ) > -1 && ua.indexOf( "like Gecko" ) > -1 && ua.indexOf( "Chrome" ) === -1 || window.document.documentElement.className.indexOf( "lt-ie9" ) > -1,
			injectref = window.document.getElementsByTagName( "link" )[0];

			function insert_css(style) {
				var fontstyle = window.document.createElement( "style" );
				fontstyle.innerHTML = style;
				if( injectref && injectref.parentNode ) {
					injectref.parentNode.insertBefore( fontstyle, injectref );
				}
				console.timeEnd("localstorage");
			}

			function load_css() {
				console.time("localstorage");
				var local_style = localStorage.getItem('zeit_webfonts');
				if (local_style && local_style.length > 0) {
					console.log("throwing in the local style");
					insert_css(local_style);
				} else {
					console.log("ajaxing");
					$.ajax({
						url: '/css/webfonts.css',
						success: (function (ajaxed_style) {
							localStorage.setItem('zeit_webfonts', ajaxed_style);
							insert_css(ajaxed_style);
						})
					});
				}
			}

			if (!old_browser) {
				load_css();
			}
		}

		return Fontloader;

	})();
	return new Fontloader();
})();
