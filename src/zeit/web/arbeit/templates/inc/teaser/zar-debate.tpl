{# this is the teaser variant of the debate module #}

{%- extends "zeit.web.arbeit:templates/inc/shared/debate.tpl" -%}

{% set block = module %}

{% block layout %}debatebox-on-cp{% endblock %}

{% block wrapper_start %}
    <aside class="{{ self.layout() }}" data-unique-id="{{ teaser.uniqueId }}" data-meetrics="{{ area.kind }}">
{% endblock %}

{% block debatebox_media %}<div class="{{ self.layout() }}__media"></div>{% endblock %}

{# TODO: Media nur per CSS, und nicht als eigenes Element (falls doch: verstecken vor Readern) #}
