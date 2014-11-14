{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}


{% block teaser_modifier %}teaser-series--smallmedia teaser-series--hasmedia{% endblock %}

{% block teaser_media_position_before_title %}
    {% set teaser_block_layout = self.layout() %}
    <div class="teaser-series__label">Serie: {{teaser.serie}}</div>
    {% include "zeit.web.site:templates/inc/teaser_asset/" +
        teaser | auto_select_asset | block_type +
        "_teaser-series-thumbnail.tpl" ignore missing with context %}
{% endblock %}
