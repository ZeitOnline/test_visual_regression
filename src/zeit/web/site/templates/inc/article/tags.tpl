{% if view.ranked_tags | length %}
	<nav class="article-tags article__item">
		<h4 class="article-tags__title">Schlagworte</h4>
		<ul class="article-tags__list">
		{% for tag in view.ranked_tags -%}
			<li><a href="#{{ tag.url_value }}" class="article-tags__link">{{ tag.label }}</a></li>
		{% endfor -%}
		</ul>
	</nav>
{% endif %}
