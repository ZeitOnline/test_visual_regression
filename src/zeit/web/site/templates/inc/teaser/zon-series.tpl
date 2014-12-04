{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}

{% block teaser_modifier -%}
    {% if not teaser|get_image_asset is none -%}teaser-series--hasmedia{%- endif %}
{%- endblock %}

{% block layout %}teaser-series{% endblock %}

{% block teaser_media_position_before_title %}
    {% set teaser_block_layout = self.layout() %}
    <div class="teaser-series__label">Serie: {{teaser.serie}}</div>
    {% include "zeit.web.site:templates/inc/teaser_asset/" +
        teaser | auto_select_asset | block_type +
        "_zon-thumbnail.tpl" ignore missing with context %}
{% endblock %}
