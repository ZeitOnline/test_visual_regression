{% if view.pagination and view.pagination.total > 1 -%}
<div class="pagination" role="navigation" aria-labeledby="pagination-title">
	<div class="pagination__a11y-title is-audible visually-hidden" id="pagination-title">Seitennavigation</div> <!-- nach unsichtbar verschieben -->

	{% if view.pagination.next_page_url -%}
	<a href="{{ view.pagination.next_page_url }}">
		<span class="pagination__button pagination__button--next">Nächste Seite</span>
	</a>

		{% if view.pagination.next_page_title -%}
		<a href="{{ view.pagination.next_page_url }}" class="pagination__nexttitle">{{ view.pagination.next_page_title }}</a>
		{%- endif %}
	{%- endif %}

	<ul class="pager">
		<li class="pager__label">Seite</li>
	{%- for url in view.pagination.pages_urls %}

		<li class="pager__number{% if loop.index == view.pagination.current %} pager__number--current{% endif %}">
			<a href="{{ url }}">{{ loop.index }}</a>
		</li>
	{%- endfor %}

		<li class="pager__all">
			<a href="{{ view.article_url }}/komplettansicht">
				<span class="pager__who">Artikel</span>
				<span class="pager__what">auf einer Seite lesen</span>
			</a>
		</li>
	</ul>
</div>
{% endif -%}
