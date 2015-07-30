{% if view.pagination and view.pagination.total > 1 -%}
<div class="article-pagination article__item" role="navigation" aria-labeledby="article-pagination-title">
	<div class="visually-hidden" id="article-pagination-title">Seitennavigation</div>

	{% if view.pagination.next_page_url -%}
		<a href="{{ view.pagination.next_page_url }}" data-id="article-pager....next-button">
			<span class="article-pagination__button article-pagination__button--next">Nächste Seite</span>
		</a>

		{% if view.pagination.next_page_title -%}
			<a href="{{ view.pagination.next_page_url }}" class="article-pagination__nexttitle" data-id="article-pager....next-title">{{ view.pagination.next_page_title }}</a>
		{%- endif %}
	{%- endif %}

	<ul class="article-pager">
		<li class="article-pager__label">Seite</li>
	{%- for page in view.pagination.pager %}

		<li class="article-pager__number{% if page == view.pagination.current %} article-pager__number--current{% endif %}">
			{%- if page -%}
				<a href="{{ view.pagination.pages_urls[page - 1] }}" data-id="article-pager....{{ page }}">{{ page }}</a>
			{%- else -%}
				<span>…</span>
			{%- endif -%}
		</li>
	{%- endfor %}

		<li class="article-pager__all">
			<a href="{{ view.content_url }}/komplettansicht" data-id="article-pager....all">
				<span class="article-pager__who">Artikel</span>
				<span class="article-pager__what">auf einer Seite lesen</span>
			</a>
		</li>
	</ul>
</div>
{% endif -%}
