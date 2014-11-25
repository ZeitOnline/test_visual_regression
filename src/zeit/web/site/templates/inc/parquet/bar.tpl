
<div class="parquet-row">
	<div class="parquet-meta">
		<div class="parquet-meta__title">
			{{ row.title }}
		</div>
		<ul class="parquet-meta__topic-links">
			{% for i in [1, 2, 3] %}
				{% set label = row.referenced_cp | get_attr('topiclink_label_%s' % i) %}
				{% set link = row.referenced_cp | get_attr('topiclink_url_%s' % i) %}
				{% if label and link %}
					<li>
						<a href="{{link}}" class="parquet-meta__topic-link">
							{{label}}
						</a>
					</li>
				{% endif %}
			{% endfor %}
		</ul>
		{% if row.read_more and row.read_more_url %}
			<a href="{{ row.read_more_url }}" class="parquet-meta__more-link">
				{{ row.read_more }}
			</a>
		{% endif %}
	</div>
	<div class="parquet-teasers">

	</div>
</div>
