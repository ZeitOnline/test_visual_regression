/* global console, alert */
(function() {
	var Fontloader;
	Fontloader = (function() {

		function Fontloader() {
			var fonts = "/css/webfonts.css",
			ua = window.navigator.userAgent,
			old_browser = ua.indexOf( "Android" ) > -1 && ua.indexOf( "like Gecko" ) > -1 && ua.indexOf( "Chrome" ) === -1 || window.document.documentElement.className.indexOf( "lt-ie9" ) > -1,
			injectref = window.document.getElementsByTagName( "link" )[0];

			function loadCSS( href ){
				// possible enhancement: check in localstorage if fonts already cached
				var fontslink = window.document.createElement( "link" );
				fontslink.rel = "stylesheet";
				fontslink.href= href;
				if( injectref && injectref.parentNode ) {
					injectref.parentNode.insertBefore( fontslink, injectref );
					// store in localstorage if not in there yet
				}
			}

			if (!old_browser) {
				loadCSS(fonts);
			}
		}

		return Fontloader;

	})();
	return new Fontloader();
})();
