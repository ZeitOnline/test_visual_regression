{% extends "zeit.web.core:templates/inc/asset/image_teaser.tpl" %}
{% import "zeit.web.site:templates/macros/layout_macro.tpl" as lama %}

{% block media_caption %}
    {{ lama.use_svg_icon('gallery', '{}__icon'.format(module_layout), view.package) }}

    <small class="{{ module_layout }}__counter">
        {{- teaser.keys() | list | length | pluralize('Keine Fotos', 'Ein Foto', '{} Fotos') -}}
    </small>

    {{ super() }}
{% endblock %}
