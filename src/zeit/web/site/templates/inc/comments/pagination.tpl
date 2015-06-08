{%- set pages = view.comments.pages %}
{%- if pages.pager %}

<div class="comment-section__item">
	<div class="pager" role="navigation" aria-labeledby="comments-pagination-title">
		<div class="visually-hidden" id="comments-pagination-title">Kommentarseiten</div>
		{% if pages.current == pages.total %}
		<a class="pager__button pager__button--previous" href="{{ view.request | append_get_params(page=pages.current-1, cid=None) }}#comments">Weitere Kommentare</a>
		{% else %}
		<a class="pager__button pager__button--next" href="{{ view.request | append_get_params(page=pages.current+1, cid=None) }}#comments">Weitere Kommentare</a>
		{% endif %}
		<ul class="pager__pages">
			{% for page in pages.pager %}
			<li class="pager__page{% if page == pages.current %} pager__page--current{% endif %}">
				{%- if page == pages.current -%}
					<span>{{ page }}</span>
				{%- elif page -%}
					<a href="{{ view.request | append_get_params(page=page, cid=None) }}#comments">{{ page }}</a>
				{%- else -%}
					<span>…</span>
				{%- endif -%}
			</li>
			{% endfor %}
		</ul>
	</div>
</div>
{%- endif %}
