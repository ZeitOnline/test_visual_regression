{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}

{% block layout %}teaser-blog{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/" +
        teaser | auto_select_asset | block_type +
        "_zon-thumbnail.tpl" ignore missing with context %}
{% endblock %}

{% block teaser_format_marker %}
	<span class="{{ self.layout() }}__marker">Blog</span>
{% endblock %}

{% block teaser_format_name %}
	<span class="{{ self.layout() }}__name">
		{{ teaser.blog.name | hide_none }}
		{% if teaser.teaserSupertitle or teaser.supertitle %} / {% endif %}
	</span>
{% endblock %}
