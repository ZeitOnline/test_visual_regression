{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}

{% block layout %}teaser-large{% endblock %}

{% block teaser_media_position_after_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "_zon-large.tpl" ignore missing with context %}
{% endblock %}
