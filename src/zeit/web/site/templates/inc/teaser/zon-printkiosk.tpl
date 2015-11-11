<article class="{% block layout %}teaser-printkiosk{% endblock %} {% if module.visible_mobile == False %} mobile-hidden{% endif %}"
    data-unique-id="{{ teaser.uniqueId }}"
    data-clicktracking="{{ area.kind }}"
    data-type="teaser">
    <a href="{{ teaser | create_url }}">
        <div class="teaser-printkiosk__figurewrapper">
            {% block teaser_media_position_before_title %}
                {% set module_layout = self.layout() %}
                <div class="{{ module_layout }}__figurewrapper">
                    {% include "zeit.web.site:templates/inc/teaser_asset/imagegroup_printkiosk.tpl" %}
                </div>
            {% endblock %}
        </div>
        <div class="teaser-printkiosk__container">
            <p class="{{ self.layout() }}__title">{{ teaser.teaserTitle }}</p>
        </div>
    </a>
</article>
