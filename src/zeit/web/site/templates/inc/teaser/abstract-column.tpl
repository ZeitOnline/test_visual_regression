{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-column{% endblock %}

{% block teaser_modifier %}{% if get_image(teaser, name='author', fallback=False) %}{{ self.layout() }}--has-media{% endif %}{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/asset/image_zon-column.tpl" %}
{% endblock %}

{% block teaser_journalistic_format %}
   <div class="{{ self.layout() }}__series-label">{{ teaser.serie.serienname }}</div>
{% endblock %}
{% block teaser_kicker %}
    <span class="{{ '%s__kicker' | format(self.layout()) | with_mods(journalistic_format, area.kind, 'zmo' if teaser is zmo_content, 'zett' if teaser is zett_content, 'zco' if teaser is zco_content) }}">
        {% block kicker_logo scoped %}
            {{ self.content_kicker_logo() }}
        {% endblock %}
        {{ teaser.teaserSupertitle or teaser.supertitle -}}
    </span>
{% endblock %}
{% block teaser_title %}
    <span class="{{ self.layout() }}__title">{{ teaser.teaserTitle or teaser.title }}</span>
{% endblock %}
