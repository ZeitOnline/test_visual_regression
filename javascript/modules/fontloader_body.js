/* global console, define */

define(['jquery'], function() {
	var fl = window.FontLoader;

	var fetch_css = function(path, identifier, version) {
		// let’s fetch font data asynchronously from the server and store it in local storage
		$.ajax({
			url: path,
			success: function (ajaxed_style, font_pack_version) {
				// we’ve got the fonts, store them in localstorage and apply them
				localStorage.setItem(fl.storage_base_string + identifier, ajaxed_style);
				localStorage.setItem(fl.storage_base_string + identifier + fl.storage_version_suffix, version);
				fl.append_css(ajaxed_style);
			}
		});
	};

	var init = function() {
		// lazy load queued fonts after document ready
		$(function() {
			for (var i in fl.scheduled_fonts) {
				if (i) {
					var pack = fl.font_dictionary[i];
					// apply fonts only if no selector present or selector returns at least one element
					if (!pack.selector || document.querySelectorAll(pack.selector).length >= 1) {
						// get font data via ajax and store
						fetch_css(fl.scheduled_fonts[i].path, fl.scheduled_fonts[i].identifier, fl.scheduled_fonts[i].version);
					}
				}
			}
		});
	};

	return {
		init: init
	};

});