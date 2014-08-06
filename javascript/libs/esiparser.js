/*
 * ESI Parser 1.00 - Poor Man's ESI
 *
 * - or - I'm tired of seeing the wrong thing in my browser while developing.
 *
 * This code provides a client-side ESI parsing capability.  It was created 
 * to provide an easier way of developing and testing sites that use ESI
 * when not behind the cache or other system that provides the ESI parsing.
 * It requires jQuery (anything after v1.2 should be fine)
 *
 * Copyright (c) 2008 Jay Kuri (jayk - cpan.org)
 *
 * Licensed under the GPL.  
 * Other licensing available upon request.
 * Date: 2008-09-17 
 * 
 */
/* Enable this line - or include it in the page you want to process 
   in order to kick off the esi_parsing. 
 */
//$(document).ready( function () { do_esi_parsing(document); });
function do_esi_parsing( element ) {
    if (element == document) { 
        // if we are processing the document element, we have
        // to get the body and head elements contents and do our 
        // esi substitution. 
        esi_strip_esi_comments($('head'));
        esi_strip_esi_comments($('body'));
    }
	var includes = esi_get_subelements_by_name(element, 'esi:include'); 
	var includes_total = includes.length+1;
	for (var i = includes.length -1 ; i >= 0 ; i-- ) {
		var include = $(includes[i]);
		var src = include.attr('src');
		var children = $(include)[0].childNodes;
		for (var j = children.length - 1; j >= 0 ; j--) {
			var child = $(children[j]).remove();
			include.after(child);
		}
		esi_get_page(include,src);
	}
	var removes = esi_get_subelements_by_name(element, 'esi:remove');
	for (var k = removes.length -1; k >=0 ; k--) {
		$(removes[k]).remove();
	}
	return includes_total;
}
function esi_get_page(element,src) {
	var self = element;
	jQuery.get(src,  function (data, status) {

	    if (data.indexOf('<!--esi') != -1) {
	        var newdata = data.replace(/\n/g,'\uffff').replace(/<!--esi(.*)-->/gm, "$1").replace(/\uffff/g,'\n');
	        data = newdata;
	    } 
		var parent;
		if (self[0] && self[0].parentNode) {
		    parent = self[0].parentNode;
		} else { 
		    return; 
		}
		var subelement = $(data).insertBefore(self);
		self.remove();
		if (data.indexOf('esi:include') != -1) {				
			do_esi_parsing(parent);
		}
	});
}
function esi_get_subelements_by_name(element,elementname) {
	var found = new Array();
	elementname = elementname.toLowerCase();
	if (element.nodeType == 9 || element.nodeType == 1) {
		var children = element.childNodes;
		for (var i = 0; i < children.length ; i++ ) {
			var elem = children[i];
			if (elem.nodeType == 1) {
				var tagname = elem.tagName.toLowerCase();
				if (tagname == elementname) {
					found.push(element.childNodes[i]);
				}
				if ( elem.childNodes.length > 0) {
					var res = esi_get_subelements_by_name(elem,elementname);
					found = found.concat(res);
				}
				
			}
		}
	}
	return found;
}

function esi_strip_esi_comments(element) {
    var reg = /<!--esi(.*)-->/gm;
    var data = $(element).html();
    if (data.indexOf('<!--esi') != -1) {
        var newdata = data.replace(/\n/g,'\uffff').replace(reg, "$1").replace(/\uffff/g,'\n');
        $(element).html(newdata);
    }
}
