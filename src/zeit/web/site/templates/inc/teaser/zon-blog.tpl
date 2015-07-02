{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-blog{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
{% endblock %}

{% block teaser_journalistic_format %}
	<span class="{{ self.layout() }}__marker">Blog</span>
	<span class="{{ self.layout() }}__name">
		{{ teaser.blog.name | hide_none }}
	</span>
{% endblock %}
