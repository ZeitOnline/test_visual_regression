<div class="parquet-row">
	<div class="parquet-row__title">
		{{ block.title }}
	</div>
	{% if block.read_more and block.read_more_url %}
		<a href="{{ block.read_more_url }}" class="parquet-row__more-link">
			{{ block.read_more }}
		</a>
	{% endif %}
</div>
