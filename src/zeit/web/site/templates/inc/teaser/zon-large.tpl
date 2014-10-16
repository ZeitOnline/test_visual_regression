{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_modifier %}teaser--hasmedia{% endblock %}
{% block teaser_heading_modifier %}teaser__heading--hasmedia{% endblock %}

{% block teaser_media_position_after_title %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "_zon-large.tpl" ignore missing with context %}
{% endblock %}
