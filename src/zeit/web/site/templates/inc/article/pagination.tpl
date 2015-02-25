{% if view.pagination and view.pagination.total > 1 -%}
<div class="article__pagination" role="navigation" aria-labeledby="pagination-title">
	<div class="paginator__a11y__title is-audible" id="pagination-title" style="display:none">Seitennavigation</div> <!-- nach unsichtbar verschieben -->

	{% if view.pagination.prev_page_url -%}
	<a href="{{ view.pagination.prev_page_url }}">
		<span class="article__pagination__button article__pagination__button--previous">Vorherige Seite</span>
	</a>
	{%- endif %}

	{% if view.pagination.next_page_url -%}
	<a href="{{ view.pagination.next_page_url }}">
		<span class="article__pagination__button article__pagination__button--next">Nächste Seite</span>
	</a>

		{% if view.pagination.next_page_title -%}
		<a href="{{ view.pagination.next_page_url }}" class="article__pagination__nexttitle">{{ view.pagination.next_page_title }}</a>
		{%- endif %}
	{%- endif %}

	<ul class="article__pager">
		<li class="article__pager__label">Seite</li>
	{%- for url in view.pagination.pages_urls %}

		<li class="article__pager__number{% if loop.index == view.pagination.current %} article__pager__number--current{% endif %}">
			<a href="{{ url }}">{{ loop.index }}</a>
		</li>
	{%- endfor %}

		<li class="article__pager__all">
			<a href="{{ view.article_url }}/komplettansicht">
				<span class="article__pager__who">Artikel</span>
				<span class="article__pager__what">auf einer Seite lesen</span>
			</a>
		</li>
	</ul>
</div>
{% endif -%}
