<article class="{% block layout %}teaser-shop{% endblock %}"
    data-unique-id="{{ teaser.uniqueId }}"
    data-clicktracking="{{ area.kind }}"
    data-type="teaser">
    <a href="{{ teaser | create_url }}">
        {% set module_layout = self.layout() %}
        {% include "zeit.web.site:templates/inc/teaser_asset/imagegroup_shop.tpl" %}
        <p class="{{ self.layout() }}__text">{{ teaser.teaserText }}</p>
    </a>
</article>
