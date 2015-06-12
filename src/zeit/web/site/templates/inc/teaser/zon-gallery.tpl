{%- extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" -%}

{% block teaser_metadata_default %}
<small class="{{ self.layout() }}__counter">
    {{ teaser.keys() | list | length | pluralize('Keine Fotos', 'Ein Foto', '{} Fotos') }}
</small>
{% endblock %}
