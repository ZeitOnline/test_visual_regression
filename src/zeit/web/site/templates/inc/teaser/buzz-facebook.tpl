{%- extends "zeit.web.site:templates/inc/teaser/buzz.tpl" -%}

{% block teaser_media_position_after_title %}
    {% with -%}
        {% set class = 'buzz-line' %}
        {% set icon = teaser_block.layout %}
        {% set label = teaser.score %}
        {% set modifier = teaser_block.layout %}
        {% include ["zeit.web.site:templates/inc/teaser_asset/annotation_" + teaser_block.layout + ".tpl",
                    "zeit.web.site:templates/inc/teaser_asset/annotation.tpl"] with context %}
    {%- endwith %}
{% endblock %}
