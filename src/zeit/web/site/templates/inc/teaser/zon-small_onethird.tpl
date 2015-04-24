{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-small-onethird{% endblock %}

{% block teaser_media_position_after_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/" +
        teaser | auto_select_asset | block_type +
        "_zon-thumbnail.tpl" ignore missing with context %}
{% endblock %}

{% block teaser_container %}
    <div class="{{ self.layout() }}__inner">
        {{ super() }}
    </div>
{% endblock %}
