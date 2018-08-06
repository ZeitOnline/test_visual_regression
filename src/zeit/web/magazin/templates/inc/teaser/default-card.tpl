{%- import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}
{%- import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama with context %}

{% set fill_color = module.background_color %}
{% if not fill_color %}
    {% set imgref = adapt(teaser, 'zeit.content.image.interfaces.IImages') %}
    {% set fill_color = imgref.fill_color if imgref else None %}
{% endif %}
{% if fill_color %}
    {% set card_style = 'background-color: #{};'.format(fill_color) -%}
{% endif %}

<article class="{% block layout %}teaser-card{% endblock %} {{ cp.advertorial_modifier(teaser.product, view.is_advertorial) | default('') }}"
         data-unique-id="{{ teaser.uniqueId }}"
         {%- block zplus_data %}{% if teaser is zplus_content %} data-zplus="zplus{% if teaser is zplus_registration_content %}-register{% endif %}"{% endif %}{% endblock %}
         {%- block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}>
    <div class="card__wrap">
        <div class="card__deck">
            {# front of card #}
            <div class="card {% block card_class %}{% endblock %}"{% if card_style %} style="{{ card_style }}"{% endif %}>

                {% if teaser.serie and not teaser.serie.column and not teaser.serie.serienname == 'Martenstein' %}
                    <div class="card__series-label">Serie: {{ teaser.serie.serienname }}</div>
                {% endif %}

                <h2>
                    <div class="card__title">
                        {% block zplus_kicker_logo %}
                            {% if teaser is zplus_abo_content %}
                                {{ lama.use_svg_icon('zplus', 'zplus-logo zplus-logo--xs', view.package, a11y=False) }}
                            {% elif teaser is zplus_registration_content and toggles('zplus_badge_gray') %}
                                {{ lama.use_svg_icon('zplus', 'zplus-logo-register zplus-logo--xs', view.package, a11y=False) }}
                            {% endif %}
                        {% endblock %}
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
