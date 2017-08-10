{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-column{% endblock %}

{% block teaser_modifier %}{% if get_image(teaser, name='author', fallback=False) %}{{ self.layout() }}--has-media{% endif %}{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/asset/image_zon-column.tpl" %}
{% endblock %}

{% block teaser_journalistic_format %}
   <div class="{{ '%s__series-label' | format(self.layout()) | with_mods(teaser | vertical_prefix ) }}">{{ teaser.serie.serienname }}</div>
{% endblock %}
