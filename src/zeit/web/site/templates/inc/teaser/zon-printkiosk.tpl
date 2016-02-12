<article class="{% block layout %}teaser-printkiosk{% endblock %}"
    data-unique-id="{{ teaser.uniqueId }}"
    data-clicktracking="{{ area.kind }}"
    data-type="teaser">
    {% set teaser_link = teaser | create_url %}
    {% if teaser_link %}<a href="{{ teaser_link }}">{% endif %}
        {% set module_layout = self.layout() %}
        {% include "zeit.web.site:templates/inc/teaser_asset/imagegroup_printkiosk.tpl" %}
        <h4 class="{{ self.layout() }}__title">{{ teaser.teaserTitle }}</h4>
    {% if teaser_link %}</a>{% endif %}
</article>
