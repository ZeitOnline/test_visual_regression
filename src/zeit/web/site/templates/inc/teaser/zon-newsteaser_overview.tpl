{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama %}
{% include "zeit.web.site:templates/inc/teaser/zon-newsteaser.tpl" %}

{% if view.advertising_enabled %}
    {% if loop.index == 10 %}
        <div class="newsteaser__ad">
            {% include "zeit.web.core:templates/inc/ads/places/desktop/place8.html" %}
            {% include "zeit.web.core:templates/inc/ads/places/mobile/place4.html" %}
        </div>
    {% endif %}
{% endif %}
