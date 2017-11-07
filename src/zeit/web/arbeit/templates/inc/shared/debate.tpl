{# this template is shared between articles and centerpages #}

{% set url = adapt(block.context, 'zeit.content.infobox.interfaces.IDebate').action_url %}

{% block wrapper_start %}
<aside class="article__item {{ self.layout() | with_mods('without-button') if not url }}">
{% endblock %}

    <div class="{{ self.layout() }}__wrapper">
        {% block debatebox_media %}{% endblock %}
        <div class="{{ self.layout() }}__container">
            <span class="{{ self.layout() }}__kicker">{{ block.title }}</span>
            <h2 class="{{ self.layout() }}__title">
                {%- if block.contents -%}
                    {% for title, text in block.contents %}
                        {{ title }}
                    {% endfor %}
                {%- endif -%}
            </h2>
            <p class="{{ self.layout() }}__text">
            {% if block.contents -%}
                {% for title, text in block.contents %}
                    {% for block in text %}
                        {{- block | safe -}}
                    {% endfor %}
                {% endfor %}
            {%- endif %}
            </p>
        </div>
    </div>

    {% if url %}
        <a href="{{ url }}" class="{{ self.layout() }}__button" data-ct-label="button">Schreiben Sie uns</a>
    {% endif %}

</aside>

{% block wrapper_end %}
</aside>
{% endblock %}
