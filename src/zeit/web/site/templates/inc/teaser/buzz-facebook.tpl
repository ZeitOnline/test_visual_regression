{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_modifier %}teaser--buzz teaser--{{ layout }}{% endblock %}

{% block teaser_heading_modifier %}teaser__heading--buzz teaser__heading--{{ layout }}{% endblock %}

{% block teaser_media_position_after_title %}
    {% include ["zeit.web.site:templates/inc/teaser_asset/annotated-icon_" + layout + ".tpl",
                "zeit.web.site:templates/inc/teaser_asset/annotated-icon.tpl"] with context %}
{% endblock %}

{% block teaser_container %}{% endblock %}
