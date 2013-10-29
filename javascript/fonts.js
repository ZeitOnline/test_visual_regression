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
				var fontslink = window.document.createElement( "link" );
				fontslink.rel = "stylesheet";
				fontslink.href= href;
				if( injectref && injectref.parentNode ) {
					injectref.parentNode.insertBefore( fontslink, injectref );
				}
			}
			alert(old_browser);
			if (!old_browser) {
				loadCSS(fonts);
			}
		}

		return Fontloader;

	})();
	return new Fontloader();
})();
