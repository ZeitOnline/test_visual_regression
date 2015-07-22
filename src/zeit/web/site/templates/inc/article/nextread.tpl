{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% set module = view.nextread %}
{% set teaser = module | first_child %}
{% set image = get_teaser_image(module, teaser) %}
{% set has_default_image = get_default_image_id() in image.uniqueId %}

{% if view.nextread %}
	<article class="nextread{% if has_default_image %} nextread--no-image{% else %} nextread--with-image{% endif %}" id="nextread">
		<a class="nextread__link" title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | create_url }}">
			<div class="nextread__lead">{{ module.lead or 'Lesen Sie jetzt' }}</div>
			{% if image and not has_default_image -%}
				{% set module_layout = 'nextread' %}
				{% include "zeit.web.site:templates/inc/teaser_asset/{}_zon-nextread.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
			{%- endif -%}
			<div class="nextread__container">
				<h2 class="nextread__heading">
					<span class="nextread__kicker">{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</span>
					<span class="nextread__title">{{ teaser.teaserTitle or teaser.title | hide_none }}</span>
				</h2>
				<div class="nextread__metadata">
					<time class="nextread__datetime" datetime="{{ teaser | mod_date | format_date('iso8601') }}">
						{{- teaser | mod_date | format_timedelta(days=356, absolute=True) | title -}}
					</time>
					{% set comments = view.comment_counts.get(teaser.uniqueId, 0) %}
					{% if comments -%}
						<span class="nextread__commentcount">
							{{- comments | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') -}}
						</span>
					{%- endif %}
				</div>
			</div>
		</a>
	</article>
{% endif %}
