<div class="parquet-row">
	<div class="parquet-meta">
		<div class="parquet-meta__title">
			{{ block.title }}
		</div>
		<ul class="parquet-meta__topiclinks">
			<li><a href="" class="parquet-meta__topiclink"></a></li>
		</ul>
		{% if block.read_more and block.read_more_url %}
			<a href="{{ block.read_more_url }}" class="parquet-meta__more-link">
				{{ block.read_more }}
			</a>
		{% endif %}
	</div>
	<div class="parquet-teasers">

	</div>
</div>
