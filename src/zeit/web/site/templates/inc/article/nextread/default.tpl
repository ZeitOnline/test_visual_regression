{% set image = get_teaser_image(module, teaser) %}
{% set has_default_image = get_default_image_id() in image.uniqueId %}
{% set is_column = teaser and teaser.serie and teaser.serie.column %}
{% set tracking_slug = 'articlebottom.editorial-nextread-large...' %}

<article class="{% block layout %}nextread{% endblock %}{% if has_default_image or is_column %} {{ self.layout() }}--no-image{% else %} {{ self.layout() }}--with-image{% endif %}" id="{{ self.layout() }}">
	<a class="{{ self.layout() }}__link" title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | create_url }}" data-id="{{ tracking_slug }}">
		<div class="{{ self.layout() }}__lead">{{ module.lead or 'Lesen Sie jetzt' }}</div>
		{% if image and not has_default_image and not is_column -%}
			{% set module_layout = self.layout() %}
			{% include "zeit.web.site:templates/inc/teaser_asset/{}_zon-nextread.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
		{%- endif -%}
		<div class="{{ self.layout() }}__container">
			<h2 class="{{ self.layout() }}__heading">
				<span class="{{ self.layout() }}__kicker">{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</span>
				<span class="{{ self.layout() }}__title">{{ teaser.teaserTitle or teaser.title | hide_none }}</span>
			</h2>
			<div class="{{ self.layout() }}__metadata">
                {{ cp.include_teaser_datetime(teaser, self.layout(), self.layout()) }}
				{% set comments = view.comment_counts.get(teaser.uniqueId, 0) %}
				{% if comments -%}
					<span class="{{ self.layout() }}__commentcount">
						{{- comments | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') -}}
					</span>
				{%- endif %}
			</div>
		</div>
	</a>
</article>
