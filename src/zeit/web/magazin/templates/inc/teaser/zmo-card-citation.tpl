{#

Teaser template for citation card

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


{% block author %}
<div class="card__author">{{ teaser.teaserTitle or teaser.title }}</div>
{% endblock %}
{% block teaser_image %}{% endblock %}
{% block teaser_text %}
<div class="card__text">
	{{ teaser.teaserText or teaser.text }}
</div>
{% endblock %}
