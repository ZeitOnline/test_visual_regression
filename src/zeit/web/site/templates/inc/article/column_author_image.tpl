{%- extends "zeit.web.site:templates/inc/linked-image_refactoring.tpl" -%}

{% set image = view.authors[0].column_teaser_image %}
{% set href = view.authors[0].href | translate_url %}

{% block mediablock %}column-heading__author-image{% endblock %}
{% block mediablock_helper %}column-heading__author-image__container{% endblock %}
{% block mediablock_link %}column-heading__author-image__link{% endblock %}
{% block mediablock_item %}column-heading__author-image__item{% endblock %}

{{ super() }}
<!-- <img data-ratio="{{ view.authors[0].column_teaser_image.ratio }}" src="{{ view.authors[0].column_teaser_image | default_image_url  }}" alt="Jack Monroe"> -->