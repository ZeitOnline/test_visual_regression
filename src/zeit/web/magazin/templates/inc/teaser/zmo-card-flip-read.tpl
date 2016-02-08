{#

Teaser template for flip/ read card

Available attributes:
    teaser

Parameters:
    card_class: to define optional front card class
    bg_image: to define background image for card
    text_class: to define optional class for card text
    teaser_text: to define content of card text
    author: to define if author is displayed
    front_action: to define button action for front side of card
    back_class: to define optional back card class
    back_action: to define button action for back side of card
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default-card.tpl" -%}

{% block card_class%}card--front{% endblock %}
{% block front_action%}flip{% endblock %}
{% block back_class%}{% endblock %}
{% block back_action%}read{% endblock %}

{% block button %}<a href="{{ teaser | create_url }}" class="card__button js-flip-card">Drehen</a>{% endblock %}

{% block back %}
<div class="card card--back js-flip-card"{% if card_style %} style="{{ card_style }}"{% endif %}>
    <h2>
		<div class="card__title">{{ teaser.teaserSupertitle }}</div>
		<div class="card__text">{{ teaser.teaserText }}</div>
	</h2>
	<a href="{{ teaser | create_url }}" class="card__button  js-stop-propagation">Lesen</a>
</div>
{% endblock %}
