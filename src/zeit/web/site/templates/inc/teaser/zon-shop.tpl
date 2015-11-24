<article class="{% block layout %}teaser-shop{% endblock %}"
    data-unique-id="http://xml.zeit.de/angebote/zeit-shop-buehne/Linkobjekte/bree-weekender"
    data-clicktracking="{{ area.kind }}"
    data-type="teaser">
    <a href="{{ teaser | create_url }}">
        <div class="{{ self.layout() }}__figurewrapper">
            {% set module_layout = self.layout() %}
            {% include "zeit.web.site:templates/inc/asset/image_teaser.tpl" %}
        </div>
        <div class="{{ self.layout() }}__container">
            <p class="{{ self.layout() }}__text">{{ teaser.teaserText }}</p>
        </div>
    </a>
</article>
