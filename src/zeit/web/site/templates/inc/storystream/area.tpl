{%- for module in area.values() %}
	{%- set module_loop = loop %}

	{# Scope: before the first module, if it is not a "was wir wissen" markdown #}
	{% if region_loop.index == 2 and module_loop.index == 1 and module.type != 'markup' %}
		{% include "zeit.web.site:templates/inc/storystream/meta/scope.tpl" %}
	{% endif %}

	{% include "zeit.web.site:templates/inc/storystream/module/includer.tpl" %}

	{# Scope: after the first module, if it is a "was wir wissen" markdown #}
	{% if region_loop.index == 2 and module_loop.index == 1 and module.type == 'markup' %}
		{% include "zeit.web.site:templates/inc/storystream/meta/scope.tpl" %}
	{% endif %}

{%- endfor %}
