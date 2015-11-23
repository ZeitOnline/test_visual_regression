<article class="{% block layout %}teaser-printkiosk{% endblock %}"
    data-unique-id="{{ teaser.uniqueId }}"
    data-clicktracking="{{ area.kind }}"
    data-type="teaser">
    {% set teaser_link = teaser | create_url %}
    {% if teaser_link %}<a href="{{ teaser_link }}">{% endif %}
        <div class="{{ self.layout() }}__figurewrapper">
            {% set module_layout = self.layout() %}
            {% include "zeit.web.site:templates/inc/teaser_asset/imagegroup_printkiosk.tpl" %}
        </div>
        <div class="{{ self.layout() }}__container">
            <p class="{{ self.layout() }}__title">{{ teaser.teaserTitle }}</p>
        </div>
    {% if teaser_link %}</a>{% endif %}
</article>
