{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-square{% endblock %}
{% block teaser_modifier %}{{ self.layout() }}--graphic{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}.tpl".format(teaser | auto_select_asset | block_type)
        ignore missing with context %}
{% endblock %}

{% block teaser_container %}
    {{ super() }}
    {% set extra = '' %}
    {% set label = 'Jetzt lesen' %}
    {% if teaser | is_gallery %}
        {# 'Alle Bilder anzeigen' is too long for .cp-area--minor tablet view #}
        {% set extra = 'Alle Bilder' %}
        {% set label = 'anzeigen' %}
    {% endif %}
    <a href="#" class="{{ self.layout() }}__button">
        <span class="{{ self.layout() }}__button-extra">{{ extra }}</span>
        {{ label }}
    </a>
{% endblock %}

{% block teaser_byline %}{% endblock %}
{% block teaser_metadata_default %}{% endblock %}
