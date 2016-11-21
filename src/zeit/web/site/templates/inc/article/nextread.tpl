{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% if module %}

	{% set teaser = module | first_child %}
	{% set teaser_type = teaser | block_type %}
	{% include
	    ["zeit.web.site:templates/inc/article/nextread/{}.tpl".format(teaser_type),
	     "zeit.web.site:templates/inc/article/nextread/default.tpl"] %}

{% endif %}
