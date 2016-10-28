{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{% include "zeit.web.site:templates/inc/teaser/zon-newsteaser.tpl" %}

{% if view.advertising_enabled %}
    {% if loop.index == 10 %}
        <div class="newsteaser__ad">
            {{ lama.adplace(view.banner(7), view) }}
            {{ lama.adplace(view.banner(4), view, mobile=True) }}
        </div>
    {% elif loop.index == 30 %}
        <div class="newsteaser__ad">
            {{ lama.adplace(view.banner(8), view) }}
        </div>
    {% endif %}
{% endif %}
