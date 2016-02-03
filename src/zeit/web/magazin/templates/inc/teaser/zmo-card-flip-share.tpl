{#

Teaser template for flip/ share card

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

{%- extends "zeit.web.magazin:templates/inc/teaser/abstract/abstract_card_teaser_template.tpl" -%}

{% block card_class %}card--front{% endblock %}
{% block bg_image %}true{% endblock %}
{% block text_class %}card__text--with-bg{% endblock %}
{% block teaser_text %}{{ teaser.teaserTitle }}{% endblock %}
{% block author %}{% endblock %}
{% block front_action %}flip{% endblock %}
{% block back_class %}js-flip-card{% endblock %}
{% block back_action %}share{% endblock %}
