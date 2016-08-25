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
    <span class="{{ '%s__kicker' | format(self.layout()) | with_mods(journalistic_format, area.kind, 'zmo' if teaser is zmo_content, 'zett' if teaser is zett_content, 'zco' if teaser is zco_content, 'zplus' if teaser is zplus_content) }}">
        {% block kicker_logo scoped %}
            {% if teaser is zplus_content %}
                {{ lama.use_svg_icon('zplus', self.layout() + '__kicker-logo--zplus svg-symbol--hide-ie', view.package, a11y=False) }}
            {% endif %}
            {% if teaser is zco_content and area.kind != 'zco-parquet' %}
                <span class="{{ self.layout() }}__kicker-logo-divider">{{ lama.use_svg_icon('logo-zco', self.layout() + '__kicker-logo--zco svg-symbol--hide-ie', 'zeit.web.campus', a11y=False) }}</span>
            {% endif %}
        {% endblock %}
        {{ teaser.teaserSupertitle or teaser.supertitle -}}
    </span>
{% endblock %}
{% block teaser_title %}
    <span class="{{ self.layout() }}__title">{{ teaser.teaserTitle or teaser.title }}</span>
{% endblock %}
