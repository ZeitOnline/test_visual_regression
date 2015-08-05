{% if view.ranked_tags | length %}
	<nav class="article-tags article__item">
		<h4 class="article-tags__title">Schlagworte</h4>
		<ul class="article-tags__list">
		{% for tag in view.ranked_tags[:6] -%}
			<li><a href="{{ request.route_url('home') }}thema/{{ tag.url_value }}" class="article-tags__link" data-id="articlebottom.article-tag.{{ loop.index }}..">{{ tag.label }}</a></li>
		{% endfor -%}
		</ul>
	</nav>
{% endif %}
