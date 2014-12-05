{# TODO: Resolve code duplication with buzz-facebook.tpl #}

{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_modifier %}teaser--buzz teaser--{{ layout }}{% endblock %}

{% block teaser_heading_modifier %}teaser__heading--buzz teaser__heading--{{ layout }}{% endblock %}

{% block teaser_media_position_before_title %}
    {% include ["zeit.web.site:templates/inc/teaser_asset/numeric_" + layout + ".tpl",
                "zeit.web.site:templates/inc/teaser_asset/numeric.tpl"] with context %}
{% endblock %}

{% block teaser_container %}{% endblock %}
