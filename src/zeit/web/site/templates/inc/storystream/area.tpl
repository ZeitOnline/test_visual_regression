{%- for module in area.values() %}
    {%- set module_loop = loop %}
    {% include "zeit.web.site:templates/inc/storystream/module/includer.tpl" %}
{%- endfor %}
