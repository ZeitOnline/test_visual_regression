{%- extends "zeit.web.site:templates/inc/image.tpl" -%}

{% block mediablock_additional_data_attributes %}data-mobile-src="{{ source | replace_variant_in_image_url('cinema') }}" data-mobile-ratio="2.33" data-mobile-variant="cinema"{% endblock %}
