<nav class="article-pagination article__item" aria-labeledby="article-pagination-title">
	<h3 class="visually-hidden" id="article-pagination-title">Seitennavigation</h3>

	{% if view.pagination.next_page_url -%}
		<a class="article-pagination__link" href="{{ view.pagination.next_page_url }}" data-id="article-pager....next-link">
			<span class="article-pagination__button article-pagination__button--next">Nächste Seite</span>
			{% if view.pagination.next_page_title -%}
			<span class="article-pagination__nexttitle">{{ view.pagination.next_page_title }}</span>
			{%- endif %}
		</a>
	{% else %}
		<a class="article-pagination__link" href="{{ request.route_url('home') }}index" data-id="article-pager....startseite">
			<span class="article-pagination__button article-pagination__button--next">Startseite</span>
		</a>
	{%- endif %}

	{% if view.pagination and view.pagination.total > 1 and not view.is_all_pages_view %}
	<ul class="article-pager">
		<li class="article-pager__label">Seite</li>

		{%- for page in view.pagination.pager %}
		<li class="article-pager__number{% if page == view.pagination.current %} article-pager__number--current{% endif %}">
			{%- if page == view.pagination.current -%}
				<span>{{ page }}</span>
			{%- elif page -%}
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
	{% endif %}
</nav>
