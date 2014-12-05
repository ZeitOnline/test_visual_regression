{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}

{% block teaser_media_position_before_title %}
    {% include ["zeit.web.site:templates/inc/teaser_asset/numeric_" + layout + ".tpl",
                "zeit.web.site:templates/inc/teaser_asset/numeric.tpl"] with context %}
{% endblock %}

{% block teaser_container %}{% endblock %}
