{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}

{% block layout %}teaser-parquet-large{% endblock %}
{% block block_type %}teaser{% endblock %}

{% block teaser_media_position_before_title %}
    {% set teaser_block_layout = self.layout() %}
    {% set teaser_block = row %}{# interim solution until CMS handles parquet more like regular teaser-blocks #}
    {% include "zeit.web.site:templates/inc/teaser_asset/" +
        teaser | auto_select_asset | block_type +
        "_zon-large.tpl" ignore missing with context %}
{% endblock %}
