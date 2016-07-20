{%- for module in area.values() %}
    {%- set module_loop = loop %}

    {# Scope: If the first module is not a "was wir wissen" markup, put the
       scope in front of it. #}
    {% if region_loop.index == 2 and module_loop.index == 1 and module.type != 'markup' %}
        {% include "zeit.web.site:templates/inc/storystream/meta/scope.tpl" %}
    {% endif %}

    {% if region_loop.index == 2 and loop.index == 2%}<a name="latest_atom"></a>{% endif %}
    {% if region_loop.index == 2 and loop.revindex == 2%}<a name="first_atom"></a>{% endif %}

    {% set layout = module | get_layout %}

    {% include [
        "zeit.web.site:templates/inc/storystream/teaser/{}.tpl".format(layout),
        "zeit.web.site:templates/inc/storystream/module/{}.html".format(layout),
        "zeit.web.site:templates/inc/storystream/teaser/default.tpl"] %}

    {# Scope: If the first module is a "was wir wissen" markup, put the
       scope behind it. #}
    {% if region_loop.index == 2 and module_loop.index == 1 and module.type == 'markup' %}
        {% include "zeit.web.site:templates/inc/storystream/meta/scope.tpl" %}
    {% endif %}

{%- endfor %}
