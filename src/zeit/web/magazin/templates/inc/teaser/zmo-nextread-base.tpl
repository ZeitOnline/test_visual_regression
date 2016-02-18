{#
Default teaser template for nextread teasers
#}

{%- set image = get_image(module, teaser, fallback=True, variant_id="wide") %}

<div class="{% block layout %}teaser-nextread{% endblock %}">
    <a title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | create_url }}">

        {% block teaser_image %}
            {% if image %}
                {% set media_caption_additional_class = 'figcaption--hidden' %}
                {% set module_layout = self.layout() %}
                {% set href = teaser | create_url %}
                {% include "zeit.web.core:templates/inc/asset/image.tpl" %}
            {% endif %}
        {% endblock %}

        {# display nextread text #}
        <div class="{{ self.layout() }}__text">
            <span class="{{ self.layout() }}__supertitle">{{ teaser.supertitle }}</span>
            <span class="{{ self.layout() }}__title">{{ teaser.title }}</span>
        </div>
    </a>
</div>



