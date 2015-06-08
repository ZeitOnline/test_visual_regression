{%- if teaser | is_zmo %}
	{%- include "zeit.web.site:templates/inc/teaser/zon-square-zmo.tpl" -%}
{%- else %}
	{%- include "zeit.web.site:templates/inc/teaser/zon-square-graphic.tpl" -%}
{%- endif %}
