{% if view.ranked_tags | length %}
    <nav class="article-tags">
        <h4 class="article-tags__title">Schlagworte</h4>
        <ul class="article-tags__list">
        {% for tag in view.ranked_tags[:6] -%}
            {% if tag.url_value %}
                <li><a href="{{ request.route_url('home') }}thema/{{ tag.url_value }}" class="article-tags__link" data-id="articlebottom.article-tag.{{ loop.index }}..{{ tag.label | format_webtrekk }}">{{ tag.label }}</a></li>
            {% else %}
                <li><span class="article-tags__link">{{ tag.label }}</span></li>
            {% endif %}
        {% endfor -%}
        </ul>
    </nav>
{% endif %}
