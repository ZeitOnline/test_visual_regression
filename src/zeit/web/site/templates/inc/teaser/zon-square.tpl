{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-square{% endblock %}
{% block teaser_modifier %}{{ self.layout() }}--graphic{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}_zon-square.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
    {% if provides(teaser, 'zeit.content.link.interfaces.ILink') and teaser.url.startswith('http://ze.tt') %}
        {% block kicker_logo %}
        {% endblock %}
        {{ lama.use_svg_icon('logo-zett-small', 'teaser-square__kicker-logo--zett', request) }}
    {% endif %}
{% endblock %}

{% block teaser_journalistic_format %}
    {%- if teaser.serie %}
        {%- if teaser.serie.column %}
           <span class="{{ self.layout() }}__series-label">{{ teaser.serie.serienname }}</span>
        {%- else %}
            <span class="{{ self.layout() }}__series-label">Serie: {{ teaser.serie.serienname }}</span>
        {%- endif %}
    {%- elif teaser.blog %}
        <span class="{{ self.layout() }}__series-label">Blog: {{ teaser.blog.name | hide_none }}</span>
    {%- endif %}
{% endblock teaser_journalistic_format %}

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
