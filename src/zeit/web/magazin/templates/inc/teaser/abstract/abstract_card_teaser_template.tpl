{#

Default teaser template for cards.

Available attributes:
    cp
    module
    teaser

All calling templates have to provide:
    card_class: to define optional front card class (None, 'string')
    bg_image: to define background image for card (None, 'string')
    text_class: to define optional class for card text (None, 'string')
    teaser_text: to define content of card text ('string')
    author: to define if author is displayed (None, 'true')
    front_action: to define button action for front side of card ('read', 'share', 'flip')
    back_class: to define optional back card class (None, 'string')
    back_action: to define button action for back side of card ('read', 'share', 'flip')
#}

{% import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}

{% set image = get_teaser_image(module, teaser) -%}

{% if module.background_color %}
    {% set card_style = 'background-color: #' + module.background_color + ';' -%}
{% else %}
    {% set card_style = '' %}
{% endif %}

{# if we have to display a bg image, prepare it here #}
{% if self.bg_image() == 'true' %}
    {% if image %}
        {% set card_style = card_style + ' background-image: url(' + image|default_image_url(image_pattern=module.layout.image_pattern) + ')' %}
    {% endif %}
{% endif %}

<div class="cp_button cp_button--card{{ cp.advertorial_modifier(teaser.product_text, view.is_advertorial) | default('') }}">
    <div class="card__wrap">
        <div class="card__deck">

            {# front of card #}
            <div class="card {{ self.card_class() }}">
                {% include "zeit.web.magazin:templates/inc/asset/image-card.tpl" %}
                <h2>
                    <div class="card__title">{{ teaser.teaserSupertitle }}</div>
                    <div class="card__text {{ self.text_class() }}">{{ self.teaser_text() }}</div>
                </h2>

                {% if self.author() == 'true' %}
                    <div class="card__author">{{ teaser.teaserTitle }}</div>
                {% endif %}

                {{ cp.teaser_card_front_action(self.front_action(), teaser|create_url) }}
            </div>

            {# back of card #}
            {% if self.front_action() == 'flip' %}
                <div class="card card--back {{ self.back_class() }}" style="background-color: #{{ module.background_color }};">
                    <h2>
                        <div class="card__title">{{ teaser.teaserSupertitle }}</div>
                        <div class="card__text">{{ teaser.teaserText }}</div>
                    </h2>

                    {{ cp.teaser_card_back_action(self.back_action(), teaser|create_url) }}
                </div>
            {% endif %}

            {# sharing functionality #}
            {% if self.back_action() == 'share' or self.front_action() == 'share' %}
                {{ cp.teaser_sharing_card(teaser) }}
            {% endif %}
        </div>
    </div>
</div>

