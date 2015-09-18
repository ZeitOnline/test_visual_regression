{% macro render_toc_label(view, page) -%}
	<strong>Seite {{ page }}</strong>
	{%- if view.pagination.pages_titles[page - 1] %} — {{ view.pagination.pages_titles[page - 1] }}
	{%- endif %}
{% endmacro %}

{% if view.pagination and view.pagination.total > 1 %}
<aside class="article-toc article__item article__item--wide">
	<div class="article-toc__container">
		<h3 class="article-toc__headline">Inhalt</h3>
		<ol class="article-toc__list">
		{%- if view.is_all_pages_view %}
			{%- set current = loop.index %}
		{%- else %}
			{%- set current = view.pagination.current %}
		{%- endif %}
		{%- for page in view.pagination.pager %}

			{% if page == current -%}
			<li class="article-toc__item article-toc__item--current">
				{{ render_toc_label(view, page) }}
			</li>
			{%- else -%}
			<li class="article-toc__item">
				<a class="article-toc__link js-scroll" href="
					{%- if view.is_all_pages_view -%}
						#seite-{{ page }}
					{%- else -%}
						{{ view.pagination.pages_urls[page - 1] }}
					{%- endif -%}
					" data-id="article-toc....{{ page }}">
					{{ render_toc_label(view, page) }}
				</a>
			</li>
			{%- endif -%}

		{% endfor %}

		</ol>
		{% if not view.is_all_pages_view -%}
		<a class="article-toc__onesie" href="{{ view.content_url }}/komplettansicht" data-id="article-toc....all">Auf einer Seite lesen</a>
		{%- endif %}

	</div>
</aside>
{% endif %}
