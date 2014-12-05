{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}

{% block teaser_media_position_after_title %}
    {% include ["zeit.web.site:templates/inc/teaser_asset/annotated-icon_" + layout + ".tpl",
                "zeit.web.site:templates/inc/teaser_asset/annotated-icon.tpl"] with context %}
{% endblock %}

{% block teaser_container %}{% endblock %}
