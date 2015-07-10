{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-fullwidth{% endblock %}

{% block teaser_modifier %}{{ self.layout()}}--blog{% endblock %}
{% block teaser_container_modifier %}{{ self.layout()}}__container--blog{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
    <div class="{{ self.layout() }}__inner-helper {{ self.layout() }}__inner-helper--blog">
	    <div class="blog-format blog-format--fullwidth">
			<span class="blog-format__marker blog-format__marker--fullwidth">Blog</span>
			<span class="blog-format__name blog-format__name--fullwidth">
				{{ teaser.blog.name | hide_none }}
			</span>
		</div>
{% endblock %}

{% block teaser_media_position_after_container %}
    </div>
{% endblock %}

{% block teaser_kicker %}
	<span class="{{ self.layout() }}__kicker {{ self.layout() }}__kicker--blog">{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</span>
{% endblock %}
