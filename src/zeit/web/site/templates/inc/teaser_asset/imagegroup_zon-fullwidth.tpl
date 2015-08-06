{%- extends "zeit.web.site:templates/inc/teaser_asset/imagegroup.tpl" -%}

{% block mediablock_additional_data_attributes %}data-mobile-src="{{ source | replace_variant_in_image_url('wide') }}" data-mobile-ratio="1.77" data-mobile-variant="wide"{% endblock %}
