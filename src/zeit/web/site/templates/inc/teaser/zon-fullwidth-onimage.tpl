{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_modifier %}teaser--ispositioned teaser--islight{% endblock %}
{% block teaser_heading_modifier %}teaser__heading--issized{% endblock %}
{% block teaser_container_modifier %}teaser__container--issized-desktop{% endblock %}

{% block teaser_media_position_before_teaser %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "-zon-fullwidth-onimage.tpl" ignore missing with context %}
{% endblock %}

{% block teaser_byline_inner %}
    {{ cp.include_teaser_byline(teaser,'teaser__byline--isinline') }}
{% endblock %}

{% block teaser_byline %}
{% endblock %}
