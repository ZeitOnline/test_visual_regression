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

{% if module.background_color %}
    {% set card_style = 'background-color: #' + module.background_color + ';' -%}
{% else %}
    {% set card_style = '' %}
{% endif %}

{% set card_teaser_url = teaser|create_url %}

<!-- advertorial-modifier? -->
<article class="teaser-card">
    <div class="card__deck">
        {# front of card #}
        <div class="card {{ self.card_class() }}" style="background-color: #{{ module.background_color }};">
            {% include "zeit.web.magazin:templates/inc/asset/image-card.tpl" %}
            <h2>
                <div class="card__title">{{ teaser.teaserSupertitle }}</div>
                <div class="card__text {{ self.text_class() }}">{{ self.teaser_text() }}</div>
            </h2>

            {% if self.author() == 'true' %}
                <div class="card__author">{{ teaser.teaserTitle }}</div>
            {% endif %}

            {% if self.front_action() == 'flip' %}
                <a href="{{ card_teaser_url }}" class="card__button js-flip-card">Drehen</a>
            {% else %}
                <a href="{{ card_teaser_url }}" class="card__button">Lesen</a>
            {% endif %}
        </div>
        {# back of card #}
        {% if self.front_action() == 'flip' %}
        <div class="card card--back {{ self.back_class() }}" style="background-color: #{{ module.background_color }};">
            <h2>
                <div class="card__title">{{ teaser.teaserSupertitle }}</div>
                <div class="card__text">{{ teaser.teaserText }}</div>
            </h2>
            
            {% if self.back_action() == 'flip' %}
                <a href="{{ card_teaser_url }}" class="card__button js-flip-card">Drehen</a>
            {% else %}
                <a href="{{url}}" class="card__button js-stop-propagation">Lesen</a>
            {% endif %}
        </div>
        {% endif %}
    </div>
</article>

