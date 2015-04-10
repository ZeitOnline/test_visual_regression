{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-parquet-large{% endblock %}
{% block block_type %}teaser{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {# set again due to scope #}
    {% set module = module %}
    {% include "zeit.web.site:templates/inc/teaser_asset/" +
        teaser | auto_select_asset | block_type +
        "_zon-large.tpl" ignore missing with context %}
{% endblock %}
