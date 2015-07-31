{% if view.ranked_tags | length %}
	<div class="article-tags article__item">
		<h6>Schlagworte</h6>
		<ul>
            <li><a href="#" class="article-tags__link">Hallo Welt</a></li>
            <li><a href="#" class="article-tags__link">Hallo Welt</a></li>
        {% for tag in view.ranked_tags -%}
            <li><a href="#{{ tag.url_value }}" class="article-tags__link">{{ tag.label }}</a></li>
        {% endfor -%}
		</ul>
	</div>
{% endif %}
