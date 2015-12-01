{% if view.pagination and view.pagination.total > 1 -%}
<div class="article-pagination article__item {% block pagination_modifier %}{% endblock %}" role="navigation" aria-labeledby="article-pagination-title">
	<div class="visually-hidden" id="article-pagination-title">Seitennavigation</div>

	{% if view.pagination.next_page_url -%}
		<a href="{{ view.pagination.next_page_url }}" data-id="article-pager....next-link">
			<span class="article-pagination__button article-pagination__button--next">Nächste Seite</span>
			{% if view.pagination.next_page_title -%}
			<span class="article-pagination__nexttitle">{{ view.pagination.next_page_title }}</span>
			{%- endif %}
		</a>
	{% else %}
		<a href="http://{{ view.request.host }}/index" data-id="article-pager....startseite">
			<span class="article-pagination__button article-pagination__button--next">Startseite</span>
		</a>
	{%- endif %}

	{% if view.request.view_name != 'komplettansicht' %}
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
</div>
{% else %}
<div class="article-pagination article__item article-pagination--komplettansicht" role="navigation" aria-labeledby="article-pagination-title">
	<div class="visually-hidden" id="article-pagination-title">Seitennavigation</div>
	<a href="http://{{ view.request.host }}/index" data-id="article-pager....startseite">
		<span class="article-pagination__button article-pagination__button--next">Startseite</span>
	</a>
</div>
{% endif -%}
