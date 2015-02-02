{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}

{% block layout %}teaser-parquet-small{% endblock %}
{% block block_type %}teaser{% endblock %}
{% set teaser_block = row %}{# interim solution until CMS handles parquet more like regular teaser-blocks #}

{% block teaser_media_position_before_title %}
    {% set teaser_block_layout = self.layout() %}
    {% set teaser_block = teaser_block %}{# set again due to scope #}
    {% include "zeit.web.site:templates/inc/teaser_asset/" +
        teaser | auto_select_asset | block_type +
        "_zon-thumbnail.tpl" ignore missing with context %}
{% endblock %}
