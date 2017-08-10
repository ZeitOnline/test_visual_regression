{# this template is shared between articles and centerpages #}

{% block wrapper_start %}
<aside class="article__item {{ self.layout() }}">
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
    <a href="{{ adapt(block.context, 'zeit.content.infobox.interfaces.IDebate').action_url }}" class="{{ self.layout() }}__button" data-ct-label="button">Schreiben Sie uns</a>
</aside>

{% block wrapper_end %}
</aside>
{% endblock %}
