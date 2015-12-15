<article class="{% block layout %}teaser-shop{% endblock %}"
    data-unique-id="{{ teaser.uniqueId }}"
    data-clicktracking="{{ area.kind }}"
    data-type="teaser">
    <a href="{{ teaser | create_url }}">
        <div class="{{ self.layout() }}__figurewrapper">
            {% set module_layout = self.layout() %}
            {% include "zeit.web.site:templates/inc/teaser_asset/imagegroup_shop.tpl" %}
        </div>
        <div class="{{ self.layout() }}__container">
            <p class="{{ self.layout() }}__text">{{ teaser.teaserText }}</p>
        </div>
    </a>
</article>
