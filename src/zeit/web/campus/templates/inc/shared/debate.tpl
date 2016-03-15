{# this template is shared between articles and centerpages #}

{% block wrapper_start %}
<aside class="article__item">
{% endblock %}

    <div class="debate">
        <span class="debate__kicker">
            {% block kicker %}
                {{ block.title }}
            {% endblock %}
        </span>
        <span class="debate__title">
            {% block title %}
                {% if block.contents -%}
                    {% for title, text in block.contents %}
                        {{ title }}
                    {% endfor %}
                {%- endif %}
            {% endblock %}
        </span>
        <span class="debate__text">
            {% if block.contents -%}
                {% block text %}
                    {% for title, text in block.contents %}
                        {% for block in text %}
                            {% set type = block | block_type %}
                            {% include [
                                "{0}:templates/inc/blocks/{1}.html".format(view.package, type),
                                "zeit.web.core:templates/inc/blocks/{0}.html".format(type)] ignore missing %}
                            {% endfor %}
                        {% endfor %}
                {% endblock %}
            {%- endif %}
        </span>
        <a class="debate__label" href="{{ adapt(teaser, 'zeit.campus.interfaces.IDebate').action_url }}">
            Mitdiskutieren
        </a>
    </div>

{% block wrapper_end %}
</aside>
{% endblock %}


