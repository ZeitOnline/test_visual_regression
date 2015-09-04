{% set module_type = module.type %}

{# get_layout is expensive (does its comment say). So we only use it if needed. #}
{% if module_type == 'teaser' %}
	{% set module_layout = module | get_layout %}
{% else %}
	{% set module_layout = None %}
{% endif %}

{% include [
	"zeit.web.site:templates/inc/storystream/module/{}_{}.tpl".format(module_type, module_layout),
	"zeit.web.site:templates/inc/storystream/module/{}.tpl".format(module_type),
    "zeit.web.site:templates/inc/storystream/module/default.tpl"
    ] ignore missing %}
