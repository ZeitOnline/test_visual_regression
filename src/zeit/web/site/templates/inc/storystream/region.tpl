<pre style="background:#ffc033;">DEBUGtpuppe: REGION</pre>
{%- for area in region.values() %}
    {%- set area_loop = loop %}
    {% include "zeit.web.site:templates/inc/storystream/area.tpl" %}
{%- endfor %}
