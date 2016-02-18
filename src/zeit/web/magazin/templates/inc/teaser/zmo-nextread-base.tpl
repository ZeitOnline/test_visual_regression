{#
Default teaser template for nextread teasers
#}

{% import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{% set image = get_teaser_image(module, teaser) %}

<div class="{% block layout %}teaser-nextread{% endblock %}{% if not image %} {{ self.layout() }}--no-img{% endif %}" style="{% block bg_image %}{% endblock %}">
    <a title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | create_url }}">

        {% block teaser_image %}
            {% if image %}
                <div class="scaled-image {{ self.layout() }}__img {{ self.layout() }}__img--{{ module.multitude }}">
                    {{ lama.insert_responsive_image(image) }}
                </div>
            {% endif %}
        {% endblock %}

        {# display nextread text #}
        <div class="{{ self.layout() }}__text {{ self.layout() }}__text--{{ module.multitude }}">
            <span class="{{ self.layout() }}__supertitle">{{ teaser.supertitle }}</span>
            <span class="{{ self.layout() }}__title">{{ teaser.title }}</span>
        </div>
    </a>
</div>



