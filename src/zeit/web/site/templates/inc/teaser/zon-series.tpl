{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-series{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    <div class="teaser-series__label">{{ teaser.serie.column and 'Kolumne' or 'Serie' }}: {{ teaser.serie.serienname }}</div>
    {% include "zeit.web.site:templates/inc/teaser_asset/" +
        teaser | auto_select_asset | block_type +
        "_zon-thumbnail.tpl" ignore missing with context %}
{% endblock %}
