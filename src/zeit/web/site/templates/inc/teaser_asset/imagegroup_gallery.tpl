{% extends "zeit.web.core:templates/inc/asset/image_teaser.tpl" %}
{% import "zeit.web.core:templates/macros/layout_macro.tpl" as lama %}

{% block media_caption %}
    {{ lama.use_svg_icon('gallery', '{}__icon'.format(module_layout), view.package) }}

    <small class="{{ module_layout }}__counter">
        {{- teaser | get_gallery_images_count | pluralize('Keine Fotos', 'Ein Foto', '{} Fotos') -}}
    </small>

    {{ super() }}
{% endblock %}
