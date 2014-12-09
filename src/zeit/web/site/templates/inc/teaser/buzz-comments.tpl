{%- extends "zeit.web.site:templates/inc/teaser/buzz.tpl" -%}

{% block teaser_media_position_after_title %}
    {% with -%}
        {% set class = 'buzz-line' %}
        {% set label = teaser.score | pluralize('%s Kommentar', '%s Kommentare') %}
        {% set modifier = layout %}
        {% include ["zeit.web.site:templates/inc/teaser_asset/annotation_" + layout + ".tpl",
                    "zeit.web.site:templates/inc/teaser_asset/annotation.tpl"] with context %}
    {%- endwith %}
{% endblock %}
