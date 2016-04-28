{%- extends "zeit.web.campus:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-wide-small{% endblock %}
{% block teaser_modifier %}
    {%- if teaser.product_text == 'Advertorial' and not view.is_advertorial %}teaser-wide-small--advertorial{% endif -%}
{% endblock %}
{% block teaser_media %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.core:templates/inc/asset/image_teaser.tpl" ignore missing %}
{% endblock %}
