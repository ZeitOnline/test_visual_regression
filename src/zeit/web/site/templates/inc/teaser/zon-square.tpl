{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-square{% endblock %}
{% block meetrics %}{{ area.kind }}{% endblock %}
{% block teaser_modifier %}{{ self.layout() }}--graphic{% endblock %}
{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}_zon-square.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
{% endblock %}

{% block teaser_container %}
    {{ super() }}
    {% set extra = '' %}
    {% set label = 'Jetzt lesen' %}
    {% if teaser | is_gallery %}
        {# 'Alle Bilder anzeigen' is too long for .cp-area--minor tablet view #}
        {% set extra = 'Alle Bilder' %}
        {% set label = 'anzeigen' %}
    {% elif teaser | is_video %}
        {# 'Jetzt lesen' makes no sense for videos #}
        {% set label = 'Video ansehen' %}
    {% endif %}
    <a href="{{ teaser.uniqueId | create_url }}" class="{{ self.layout() }}__button">
        <span class="{{ self.layout() }}__button-extra">{{ extra }}</span>
        {{ label }}
    </a>
{% endblock %}

{% block teaser_byline %}{% endblock %}
{% block teaser_metadata_default %}{% endblock %}
