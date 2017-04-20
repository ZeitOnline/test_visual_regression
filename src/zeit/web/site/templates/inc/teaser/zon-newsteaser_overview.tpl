{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{% include "zeit.web.site:templates/inc/teaser/zon-newsteaser.tpl" %}

{% if view.advertising_enabled %}
    {% if loop.index == 10 %}
        <div class="newsteaser__ad">
            {% include "zeit.web.core:templates/inc/ads/places/desktop/place7.html" %}
            {% include "zeit.web.core:templates/inc/ads/places/mobile/place4.html" %}
        </div>
    {% elif loop.index == 30 %}
        <div class="newsteaser__ad">
            {% include "zeit.web.core:templates/inc/ads/places/desktop/place8.html" %}
        </div>
    {% endif %}
{% endif %}
