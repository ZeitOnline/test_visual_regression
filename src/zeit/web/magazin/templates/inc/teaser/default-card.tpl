{%- import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}

{% set image = get_teaser_image(module, teaser) %}

{% if module.background_color %}
    {% set card_style = 'background-color: #{};'.format(module.background_color) -%}
{% endif %}

<article class="{% block layout %}teaser-card{% endblock %} {{ cp.advertorial_modifier(teaser.product_text, view.is_advertorial) | default('') }}"
         data-unique-id="{{ teaser.uniqueId }}"
         {% block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}
         data-clicktracking="{{ area.kind }}"
         {% block teaser_attributes %}{% endblock %}>
    <div class="card__wrap">
        <div class="card__deck">
            {# front of card #}
            <div class="card {% block card_class %}{% endblock %}"{% if card_style %} style="{{ card_style }}"{% endif %}>
                <h2>
                    <div class="card__title">
                        {{ teaser.teaserSupertitle or teaser.supertitle }}
                    </div>
                    {% block teaser_image %}
                        {% include "zeit.web.magazin:templates/inc/asset/image-card.tpl" %}
                    {% endblock %}
                    {% block teaser_text %}
                    <div class="card__text">
                        {{ teaser.teaserTitle or teaser.title }}
                    </div>
                    {% endblock %}
                </h2>

                {% block author %}{% endblock %}
                
                {% block button %}<a href="{{ teaser | create_url }}" class="card__button">Lesen</a>{% endblock %}
            </div>
            {# back of card #}
            {% block back %}{% endblock %}
        </div>
    </div>
</article>
