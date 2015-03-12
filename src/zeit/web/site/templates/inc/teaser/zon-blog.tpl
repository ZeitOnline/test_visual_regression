{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}

{% block layout %}teaser-blog{% endblock %}

{% block teaser_media_position_before_title %}
    {% set teaser_block_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/" +
        teaser | auto_select_asset | block_type +
        "_zon-thumbnail.tpl" ignore missing with context %}
{% endblock %}

{% block teasaer_format_marker %}
	<span class="{{ self.layout() }}__marker">Blog</span>
{% endblock %}

{% block teasaer_format_name %}
	<span class="{{ self.layout() }}__name">{{ teaser.blog.name | hide_none }}</span>
{% endblock %}
