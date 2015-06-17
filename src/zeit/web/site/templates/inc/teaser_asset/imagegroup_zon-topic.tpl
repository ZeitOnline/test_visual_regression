{%- extends "zeit.web.site:templates/inc/teaser_asset/imagegroup.tpl" -%}
{% if area.referenced_cp is not none %}
	{% set teaser = area.referenced_cp %}
{% endif %}
