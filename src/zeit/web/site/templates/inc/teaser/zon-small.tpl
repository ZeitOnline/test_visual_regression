{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_modifier %}teaser--small teaser--smallmedia teaser--hasmedia{% endblock %}
{% block teaser_heading_modifier %}teaser__heading__small{% endblock %}

{% block teaser_media_position_before_title %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "-zon-thumbnail.tpl" ignore missing with context %}
{% endblock %}
