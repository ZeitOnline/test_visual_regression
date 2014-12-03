
<div class="parquet-row">
	<div class="parquet-meta">
		<div class="parquet-meta__title">
			{{ row.title }}
		</div>
		<ul class="parquet-meta__topic-links">
			{% for label, link in topiclinks(row.referenced_cp) %}
				<li>
					<a href="{{link}}" class="parquet-meta__topic-link">
						{{label}}
					</a>
				</li>
			{% endfor %}
		</ul>
		{% if row.read_more and row.read_more_url %}
			<a href="{{ row.read_more_url }}" class="parquet-meta__more-link">
				{{ row.read_more }}
			</a>
		{% endif %}
	</div>
	<ul class="parquet-teasers">
		{% for teaser in row -%}
			{% if loop.index <= row.display_amount %}
              {% include
                    [
                    "zeit.web.site:templates/inc/parquet/parquet-regular.tpl",
                    "zeit.web.site:templates/inc/teaser/default_refactoring.tpl"
                    ] %}
			{% endif %}
        {% endfor %}
	</ul>
</div>
