{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-small{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}_zon-thumbnail.tpl".format(teaser | auto_select_asset | block_type)
        ignore missing with context %}
{% endblock %}
