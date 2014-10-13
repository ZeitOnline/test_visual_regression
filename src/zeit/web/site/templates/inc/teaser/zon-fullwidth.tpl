{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_modifier %}teaser--hasmedia teaser--iscentered{% endblock %}
{% block teaser_heading_modifier %}teaser__heading--hasmedia teaser__heading--issized{% endblock %}
{% block teaser_container_modifier %}teaser__container--issized{% endblock %}

{% block teaser_media_position_after_title %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "-zon-fullwidth.tpl" ignore missing with context %}
{% endblock %}

{% block teaser_metadata_head %}
    <div class="teaser__metadata teaser__metadata--ishead">
        {{ cp.include_teaser_datetime() }}
        {{ cp.include_teaser_commentcount(teaser) }}
    </div>
{% endblock %}

{% block teaser_metadata_default %}
{% endblock %}

